import httpx
from typing import Dict, Optional, List
from app.config import settings
import hashlib
import hmac
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LemonsqueezyService:
    BASE_URL = "https://api.lemonsqueezy.com/v1"
    
    def __init__(self):
        self.api_key = settings.LEMONSQUEEZY_API_KEY
        self.store_id = settings.LEMONSQUEEZY_STORE_ID
        self.webhook_secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET
        
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for Lemonsqueezy API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def create_checkout(
        self, 
        variant_id: str, 
        user_email: str, 
        user_id: str,
        custom_data: Optional[Dict] = None
    ) -> str:
        """Create checkout session for subscription"""
        
        checkout_data = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "store_id": int(self.store_id),
                    "variant_id": int(variant_id),
                    "custom_data": {
                        "user_id": user_id,
                        **(custom_data or {})
                    },
                    "product_options": {
                        "redirect_url": f"{settings.FRONTEND_URL}/dashboard?success=true",
                        "receipt_button_text": "Go to Dashboard",
                        "receipt_thank_you_note": "Thank you for subscribing to FormFlow AI! Your account has been upgraded.",
                    },
                    "checkout_data": {
                        "email": user_email,
                        "custom": {
                            "user_id": user_id
                        }
                    },
                    "expires_at": None,  # No expiration
                    "preview": True,  # Allow preview before payment
                    "test_mode": settings.DEBUG  # Use test mode in development
                }
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/checkouts",
                    headers=self._get_headers(),
                    json=checkout_data
                )
                response.raise_for_status()
                
                data = response.json()
                checkout_url = data["data"]["attributes"]["url"]
                
                logger.info(f"Created checkout for user {user_id}: {checkout_url}")
                return checkout_url
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to create checkout for user {user_id}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to create checkout: {str(e)}")
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details from Lemonsqueezy"""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/subscriptions/{subscription_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                return response.json()["data"]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get subscription {subscription_id}: {e}")
            return None
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription"""
        
        cancel_data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": {
                    "cancelled": True
                }
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.BASE_URL}/subscriptions/{subscription_id}",
                    headers=self._get_headers(),
                    json=cancel_data
                )
                response.raise_for_status()
                
                logger.info(f"Successfully cancelled subscription {subscription_id}")
                return True
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            return False
    
    async def update_subscription(
        self, 
        subscription_id: str, 
        updates: Dict
    ) -> Optional[Dict]:
        """Update subscription details"""
        
        update_data = {
            "data": {
                "type": "subscriptions",
                "id": subscription_id,
                "attributes": updates
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.patch(
                    f"{self.BASE_URL}/subscriptions/{subscription_id}",
                    headers=self._get_headers(),
                    json=update_data
                )
                response.raise_for_status()
                
                return response.json()["data"]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to update subscription {subscription_id}: {e}")
            return None
    
    async def get_invoices(self, subscription_id: str) -> List[Dict]:
        """Get invoices for a subscription"""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/subscriptions/{subscription_id}/invoices",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                return response.json()["data"]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to get invoices for subscription {subscription_id}: {e}")
            return []
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Lemonsqueezy webhook signature"""
        
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured - skipping signature verification")
            return True
        
        try:
            # Lemonsqueezy sends the signature as hex
            expected = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def create_customer_portal(self, subscription_id: str) -> Optional[str]:
        """Create customer portal URL for subscription management"""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/subscriptions/{subscription_id}/customer-portal",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                return data["data"]["attributes"]["url"]
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to create customer portal for subscription {subscription_id}: {e}")
            return None

class PlanLimitsService:
    """Service for managing plan limits and enforcement"""
    
    # Plan configurations
    PLAN_CONFIGS = {
        "FREE": {
            "max_forms": 3,
            "max_submissions_per_month": 100,
            "max_dashboard_views_per_month": 500,
            "max_api_calls_per_month": 1000,
            "max_storage_mb": 100,
            "custom_branding": False,
            "api_access": False,
            "priority_support": False,
            "white_label": False,
            "custom_integrations": False,
            "sla_guarantee": False
        },
        "PRO": {
            "max_forms": 999,
            "max_submissions_per_month": 1000,
            "max_dashboard_views_per_month": 10000,
            "max_api_calls_per_month": 10000,
            "max_storage_mb": 1000,
            "custom_branding": True,
            "api_access": True,
            "priority_support": True,
            "white_label": True,
            "custom_integrations": False,
            "sla_guarantee": False
        },
        "BUSINESS": {
            "max_forms": 9999,
            "max_submissions_per_month": 10000,
            "max_dashboard_views_per_month": 100000,
            "max_api_calls_per_month": 100000,
            "max_storage_mb": 10000,
            "custom_branding": True,
            "api_access": True,
            "priority_support": True,
            "white_label": True,
            "custom_integrations": True,
            "sla_guarantee": True
        }
    }
    
    @classmethod
    def get_plan_limits(cls, plan_type: str) -> Dict:
        """Get limits for a specific plan"""
        return cls.PLAN_CONFIGS.get(plan_type.upper(), cls.PLAN_CONFIGS["FREE"])
    
    @classmethod
    def can_create_form(cls, plan_type: str, current_form_count: int) -> bool:
        """Check if user can create another form"""
        limits = cls.get_plan_limits(plan_type)
        return current_form_count < limits["max_forms"]
    
    @classmethod
    def can_accept_submission(cls, plan_type: str, current_submissions: int) -> bool:
        """Check if user can accept another submission this month"""
        limits = cls.get_plan_limits(plan_type)
        return current_submissions < limits["max_submissions_per_month"]
    
    @classmethod
    def has_feature(cls, plan_type: str, feature: str) -> bool:
        """Check if plan has a specific feature"""
        limits = cls.get_plan_limits(plan_type)
        return limits.get(feature, False)