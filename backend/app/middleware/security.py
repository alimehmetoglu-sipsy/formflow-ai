from fastapi import FastAPI, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import time
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY" 
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only add HSTS in production with HTTPS
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.openai.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(t > current_time - 60 for t in timestamps)
        }
        
        # Check rate limit
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove timestamps older than 1 minute
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if t > current_time - 60
        ]
        
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return StarletteResponse(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        self.requests[client_ip].append(current_time)
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Client: {request.client.host}"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

def setup_security(app: FastAPI):
    """Configure security middleware for the FastAPI app"""
    
    # Trusted hosts
    if not settings.DEBUG:
        allowed_hosts = [
            "formflow.ai", 
            "*.formflow.ai", 
            "*.railway.app",
            "*.render.com"
        ]
    else:
        allowed_hosts = ["*"]  # Allow all in development
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    # Session security
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        https_only=not settings.DEBUG,
        same_site="strict" if not settings.DEBUG else "lax",
        max_age=86400  # 24 hours
    )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting (only in production)
    if not settings.DEBUG:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("✅ Security middleware configured")