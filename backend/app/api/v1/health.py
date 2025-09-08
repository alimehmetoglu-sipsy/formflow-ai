from fastapi import APIRouter, status, Depends
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings
import redis
import asyncio

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict:
    """Check if all services are ready"""
    checks = {
        "database": False,
        "redis": False
    }
    errors = []
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        errors.append(f"Database error: {str(e)}")
    
    # Check Redis connection
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = True
    except Exception as e:
        errors.append(f"Redis error: {str(e)}")
    
    all_ready = all(checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "errors": errors if errors else None
    }