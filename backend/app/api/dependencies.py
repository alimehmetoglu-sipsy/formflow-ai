from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, PlanType
from app.config import settings
from app.services.auth import AuthService
from datetime import datetime, timedelta
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Legacy functions for backward compatibility
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token (legacy - use AuthService instead)"""
    return AuthService.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user ID (legacy - use AuthService instead)"""
    payload = AuthService.verify_token(token)
    if payload:
        return payload.get("sub")
    return None

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Use AuthService for token verification
    payload = AuthService.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account deactivated",
        )
    
    return user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    
    if not credentials:
        return None
    
    payload = AuthService.verify_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    user = AuthService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        return None
    
    return user

# Enhanced dependency functions for authentication system

async def get_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require user to be verified"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

async def require_plan(allowed_plans: List[PlanType]):
    """Create dependency that requires specific subscription plan(s)"""
    async def _require_plan(current_user: User = Depends(get_verified_user)) -> User:
        if current_user.plan_type not in allowed_plans:
            plan_names = [plan.value for plan in allowed_plans]
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Insufficient plan",
                    "message": f"This feature requires {' or '.join(plan_names)} plan",
                    "current_plan": current_user.plan_type.value,
                    "required_plans": plan_names,
                    "upgrade_required": True
                }
            )
        return current_user
    return _require_plan

# Common plan requirements (these will be function factories)
def get_require_pro_plan():
    return require_plan([PlanType.PRO, PlanType.BUSINESS])

def get_require_business_plan():
    return require_plan([PlanType.BUSINESS])

def get_require_any_paid_plan():
    return require_plan([PlanType.PRO, PlanType.BUSINESS])

async def require_onboarding_complete(
    current_user: User = Depends(get_verified_user)
) -> User:
    """Require user to have completed onboarding"""
    if not current_user.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Onboarding incomplete",
                "message": "Please complete your account setup",
                "onboarding_required": True
            }
        )
    return current_user

async def require_typeform_connection(
    current_user: User = Depends(require_onboarding_complete)
) -> User:
    """Require user to have Typeform connected"""
    if not current_user.typeform_connected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Typeform not connected",
                "message": "Please connect your Typeform account",
                "typeform_connection_required": True
            }
        )
    return current_user

# Admin dependencies (for future use)
async def require_admin(
    current_user: User = Depends(get_verified_user)
) -> User:
    """Require user to be admin (placeholder - would check admin role)"""
    # In production, check if user has admin role
    # For now, just require business plan as proxy
    if current_user.plan_type != PlanType.BUSINESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user