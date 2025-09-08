from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus
from app.api.dependencies import get_current_user
from app.services.auth import AuthService

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class UserProfile(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserStats(BaseModel):
    forms_created: int
    submissions_received: int
    dashboards_viewed: int
    plan_type: str
    account_age_days: int

# User profile endpoints
@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "plan_type": current_user.plan_type.value,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "oauth_provider": current_user.oauth_provider,
        "onboarding_completed": current_user.onboarding_completed,
        "typeform_connected": current_user.typeform_connected
    }

@router.patch("/me")
async def update_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    updated_fields = []
    
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
        updated_fields.append("full_name")
    
    if profile_data.avatar_url is not None:
        current_user.avatar_url = profile_data.avatar_url
        updated_fields.append("avatar_url")
    
    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    db.commit()
    
    logger.info(f"User {current_user.id} updated profile fields: {', '.join(updated_fields)}")
    
    return {
        "message": "Profile updated successfully",
        "updated_fields": updated_fields
    }

@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Check if user has a password (not OAuth-only user)
    if not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth-only accounts"
        )
    
    # Verify current password
    if not current_user.verify_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = User.hash_password(password_data.new_password)
    db.commit()
    
    logger.info(f"User {current_user.id} changed password")
    
    return {"message": "Password changed successfully"}

@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user account statistics"""
    
    from datetime import datetime
    account_age = (datetime.utcnow() - current_user.created_at).days
    
    # In a complete implementation, you'd query actual form and dashboard data
    # For now, return mock data
    stats = {
        "user_id": current_user.id,
        "plan_type": current_user.plan_type.value,
        "account_age_days": account_age,
        "created_at": current_user.created_at,
        "forms_created": 0,  # Would query Form table
        "submissions_received": 0,  # Would query submissions
        "dashboards_viewed": 0,  # Would query dashboard views
        "storage_used_mb": 0,  # Would calculate actual storage
        "api_calls_this_month": 0,  # Would query usage table
        "typeform_connected": current_user.typeform_connected,
        "onboarding_completed": current_user.onboarding_completed
    }
    
    return stats

@router.get("/me/subscription")
async def get_user_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user subscription information"""
    
    # Get active subscription
    subscription = db.query(Subscription).filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        return {
            "has_subscription": False,
            "plan_type": current_user.plan_type.value,
            "message": "No active subscription found"
        }
    
    return {
        "has_subscription": True,
        "subscription_id": subscription.id,
        "plan_type": subscription.plan_type.value,
        "plan_name": subscription.plan_name,
        "status": subscription.status.value,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "trial_end": subscription.trial_end,
        "cancel_at": subscription.cancel_at,
        "cancelled_at": subscription.cancelled_at,
        "unit_price": subscription.unit_price / 100,  # Convert cents to dollars
        "currency": subscription.currency
    }

@router.delete("/me")
async def delete_account(
    confirmation: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account (requires confirmation)"""
    
    if confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account deletion requires confirmation string 'DELETE'"
        )
    
    # Cancel active subscription if exists
    subscription = db.query(Subscription).filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if subscription:
        # In production, cancel the subscription with payment provider
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        logger.info(f"Cancelled subscription {subscription.id} for account deletion")
    
    # In a complete implementation, you'd delete related data:
    # - Forms created by user
    # - Dashboards created by user  
    # - Usage records
    # - Webhooks/API keys
    # etc.
    
    # For now, just deactivate the account
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}@deleted.local"  # Anonymize email
    
    db.commit()
    
    logger.warning(f"User account {current_user.id} marked for deletion")
    
    return {
        "message": "Account deletion initiated. Your data will be removed within 30 days.",
        "user_id": current_user.id
    }

@router.post("/me/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Temporarily deactivate account"""
    
    current_user.is_active = False
    db.commit()
    
    logger.info(f"User {current_user.id} deactivated account")
    
    return {"message": "Account deactivated successfully"}

@router.post("/me/reactivate")
async def reactivate_account(
    credentials: dict,  # Would contain login credentials
    db: Session = Depends(get_db)
):
    """Reactivate deactivated account"""
    
    # This would typically be called from login endpoint
    # when user tries to login with deactivated account
    
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password required for reactivation"
        )
    
    user = AuthService.authenticate_user(db, email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already active"
        )
    
    user.is_active = True
    db.commit()
    
    logger.info(f"User {user.id} reactivated account")
    
    return {"message": "Account reactivated successfully"}

# Admin endpoints (would require admin role in production)
@router.get("/admin/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    
    # In production, check if current_user is admin
    # For now, just return basic info
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "plan_type": user.plan_type.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "onboarding_completed": user.onboarding_completed
            }
            for user in users
        ],
        "total": db.query(User).count(),
        "skip": skip,
        "limit": limit
    }

# Utility endpoints
@router.post("/me/resend-verification")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Resend email verification"""
    
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Send verification email
    from app.api.v1.auth import send_verification_email
    background_tasks.add_task(send_verification_email, current_user.email, current_user.id)
    
    return {"message": "Verification email sent"}

@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent user activity"""
    
    # In production, this would query an activity/audit log
    # For now, return basic account info
    
    return {
        "user_id": current_user.id,
        "last_login": None,  # Would track this in production
        "recent_actions": [],  # Would query activity log
        "account_created": current_user.created_at,
        "profile_updated": current_user.updated_at,
        "login_count": 0,  # Would track this
        "device_info": "Not tracked"  # Would track devices/sessions
    }