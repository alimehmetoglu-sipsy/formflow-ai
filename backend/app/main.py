from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
from app.api.v1 import health, webhooks, dashboards, billing, auth, users, onboarding, templates
from app.monitoring import setup_monitoring
from app.middleware.security import setup_security

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        setup_monitoring()
    except Exception as e:
        print(f"Warning: Could not setup monitoring: {e}")
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        # Continue anyway for Cloud Run
    
    print(f"🚀 {settings.APP_NAME} v{settings.VERSION} started successfully!")
    yield
    # Shutdown
    print(f"👋 {settings.APP_NAME} shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Transform forms into AI-powered dashboards",
    version=settings.VERSION,
    lifespan=lifespan
)

# Setup security middleware
setup_security(app)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["dashboards"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["billing"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(onboarding.router, prefix="/api/v1", tags=["onboarding"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancer"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": settings.APP_NAME
    }