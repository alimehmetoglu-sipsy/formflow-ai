from datetime import datetime
from sqlalchemy.orm import Session
from app.models.subscription import Usage, PlanType
from app.models.user import User
from app.services.payment import PlanLimitsService
from fastapi import HTTPException
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class UsageTracker:
    """Track and enforce usage limits for different plans"""
    
    @staticmethod
    def get_current_month() -> str:
        """Get current month in YYYY-MM format"""
        return datetime.utcnow().strftime("%Y-%m")
    
    @staticmethod
    def get_or_create_usage(user_id: str, db: Session) -> Usage:
        """Get or create usage record for current month"""
        month = UsageTracker.get_current_month()
        
        usage = db.query(Usage).filter_by(
            user_id=user_id,
            month=month
        ).first()
        
        if not usage:
            # Find user's active subscription
            from app.models.subscription import Subscription, SubscriptionStatus
            subscription = db.query(Subscription).filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
            
            usage = Usage(
                user_id=user_id,
                subscription_id=subscription.id if subscription else None,
                month=month
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        return usage
    
    @staticmethod
    async def track_form_creation(user_id: str, db: Session) -> None:
        """Track when user creates a form and check limits"""
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        usage = UsageTracker.get_or_create_usage(user_id, db)
        
        # Check if user can create more forms
        if not PlanLimitsService.can_create_form(user.plan_type.value, usage.form_count):
            limits = PlanLimitsService.get_plan_limits(user.plan_type.value)
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Form limit exceeded",
                    "message": f"You've reached your plan limit of {limits['max_forms']} forms.",
                    "current_count": usage.form_count,
                    "limit": limits['max_forms'],
                    "plan": user.plan_type.value,
                    "upgrade_required": True
                }
            )
        
        # Increment form count
        usage.form_count += 1
        db.commit()
        
        logger.info(f"User {user_id} created form. Count: {usage.form_count}")
    
    @staticmethod
    async def track_submission(user_id: str, db: Session) -> None:
        """Track when a form receives a submission"""
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return  # Don't block submissions if user not found
        
        usage = UsageTracker.get_or_create_usage(user_id, db)
        
        # Check submission limits
        if not PlanLimitsService.can_accept_submission(user.plan_type.value, usage.submission_count):
            limits = PlanLimitsService.get_plan_limits(user.plan_type.value)
            logger.warning(
                f"User {user_id} exceeded submission limit. "
                f"Count: {usage.submission_count}, Limit: {limits['max_submissions_per_month']}"
            )
            # Don't block submission but log for billing/notification purposes
        
        # Increment submission count
        usage.submission_count += 1
        db.commit()
        
        logger.info(f"User {user_id} received submission. Count: {usage.submission_count}")
    
    @staticmethod
    async def track_dashboard_view(user_id: str, db: Session) -> None:
        """Track dashboard views"""
        usage = UsageTracker.get_or_create_usage(user_id, db)
        usage.dashboard_views += 1
        db.commit()
    
    @staticmethod
    async def track_api_call(user_id: str, db: Session) -> None:
        """Track API calls"""
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return
        
        usage = UsageTracker.get_or_create_usage(user_id, db)
        
        # Check API limits
        limits = PlanLimitsService.get_plan_limits(user.plan_type.value)
        if usage.api_calls >= limits['max_api_calls_per_month']:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "API limit exceeded",
                    "message": f"You've reached your monthly limit of {limits['max_api_calls_per_month']} API calls.",
                    "current_count": usage.api_calls,
                    "limit": limits['max_api_calls_per_month'],
                    "plan": user.plan_type.value
                }
            )
        
        usage.api_calls += 1
        db.commit()
    
    @staticmethod
    def get_usage_summary(user_id: str, db: Session) -> dict:
        """Get usage summary for user"""
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return {}
        
        usage = UsageTracker.get_or_create_usage(user_id, db)
        limits = PlanLimitsService.get_plan_limits(user.plan_type.value)
        
        return {
            "month": usage.month,
            "plan": user.plan_type.value,
            "usage": {
                "forms": {
                    "current": usage.form_count,
                    "limit": limits['max_forms'],
                    "percentage": min(100, (usage.form_count / limits['max_forms']) * 100)
                },
                "submissions": {
                    "current": usage.submission_count,
                    "limit": limits['max_submissions_per_month'],
                    "percentage": min(100, (usage.submission_count / limits['max_submissions_per_month']) * 100)
                },
                "dashboard_views": {
                    "current": usage.dashboard_views,
                    "limit": limits['max_dashboard_views_per_month'],
                    "percentage": min(100, (usage.dashboard_views / limits['max_dashboard_views_per_month']) * 100)
                },
                "api_calls": {
                    "current": usage.api_calls,
                    "limit": limits['max_api_calls_per_month'],
                    "percentage": min(100, (usage.api_calls / limits['max_api_calls_per_month']) * 100)
                },
                "storage": {
                    "current": usage.storage_used,
                    "limit": limits['max_storage_mb'],
                    "percentage": min(100, (usage.storage_used / limits['max_storage_mb']) * 100)
                }
            },
            "limits": limits,
            "warnings": UsageTracker._get_usage_warnings(usage, limits)
        }
    
    @staticmethod
    def _get_usage_warnings(usage: Usage, limits: dict) -> list:
        """Get usage warnings for approaching limits"""
        warnings = []
        
        # Check each usage metric
        if usage.form_count / limits['max_forms'] > 0.8:
            warnings.append({
                "type": "form_limit",
                "message": f"You're using {usage.form_count} of {limits['max_forms']} forms.",
                "severity": "warning" if usage.form_count / limits['max_forms'] < 0.9 else "critical"
            })
        
        if usage.submission_count / limits['max_submissions_per_month'] > 0.8:
            warnings.append({
                "type": "submission_limit",
                "message": f"You're using {usage.submission_count} of {limits['max_submissions_per_month']} monthly submissions.",
                "severity": "warning" if usage.submission_count / limits['max_submissions_per_month'] < 0.9 else "critical"
            })
        
        if usage.api_calls / limits['max_api_calls_per_month'] > 0.8:
            warnings.append({
                "type": "api_limit",
                "message": f"You're using {usage.api_calls} of {limits['max_api_calls_per_month']} monthly API calls.",
                "severity": "warning" if usage.api_calls / limits['max_api_calls_per_month'] < 0.9 else "critical"
            })
        
        return warnings
    
    @staticmethod
    def check_feature_access(user: User, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        return PlanLimitsService.has_feature(user.plan_type.value, feature)
    
    @staticmethod
    def require_feature(user: User, feature: str, feature_name: str = None) -> None:
        """Require a specific feature or raise HTTPException"""
        if not UsageTracker.check_feature_access(user, feature):
            feature_display = feature_name or feature.replace('_', ' ').title()
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Feature not available",
                    "message": f"{feature_display} is not available on your current plan.",
                    "feature": feature,
                    "plan": user.plan_type.value,
                    "upgrade_required": True
                }
            )