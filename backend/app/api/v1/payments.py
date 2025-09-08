from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.auth import get_current_user
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

router = APIRouter()

def verify_lemonsqueezy_signature(payload: bytes, signature: str) -> bool:
    """Verify LemonSqueezy webhook signature"""
    if not settings.LEMONSQUEEZY_WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    
    expected = hmac.new(
        settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/webhook/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle LemonSqueezy webhook events"""
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature
    signature = request.headers.get("X-Signature")
    if signature and not verify_lemonsqueezy_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    try:
        data = json.loads(body)
        event_type = data.get("meta", {}).get("event_name")
        event_data = data.get("data", {})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook data: {str(e)}")
    
    # Handle different event types
    if event_type == "subscription_created":
        # New subscription
        user_email = event_data.get("attributes", {}).get("user_email")
        variant_id = event_data.get("attributes", {}).get("variant_id")
        
        # Update user subscription status
        user = db.query(User).filter_by(email=user_email).first()
        if user:
            if variant_id == settings.LEMONSQUEEZY_PRO_VARIANT_ID:
                user.subscription_tier = "pro"
            elif variant_id == settings.LEMONSQUEEZY_BUSINESS_VARIANT_ID:
                user.subscription_tier = "business"
            else:
                user.subscription_tier = "starter"
            
            user.subscription_status = "active"
            user.subscription_id = event_data.get("id")
            db.commit()
    
    elif event_type == "subscription_cancelled":
        # Subscription cancelled
        subscription_id = event_data.get("id")
        user = db.query(User).filter_by(subscription_id=subscription_id).first()
        if user:
            user.subscription_status = "cancelled"
            db.commit()
    
    elif event_type == "subscription_resumed":
        # Subscription resumed
        subscription_id = event_data.get("id")
        user = db.query(User).filter_by(subscription_id=subscription_id).first()
        if user:
            user.subscription_status = "active"
            db.commit()
    
    return {"status": "success"}

@router.get("/plans")
async def get_pricing_plans():
    """Get available pricing plans"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "features": [
                    "Up to 10 forms per month",
                    "Basic AI dashboard templates",
                    "24-hour data retention",
                    "Community support"
                ],
                "limitations": {
                    "forms_per_month": 10,
                    "data_retention_hours": 24,
                    "ai_model": "gpt-3.5-turbo"
                }
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": 29,
                "variant_id": settings.LEMONSQUEEZY_PRO_VARIANT_ID,
                "features": [
                    "Unlimited forms",
                    "Advanced AI with GPT-4",
                    "Unlimited data retention",
                    "Priority support",
                    "Custom branding",
                    "Export to PDF/Excel"
                ],
                "limitations": {
                    "forms_per_month": -1,  # Unlimited
                    "data_retention_hours": -1,  # Unlimited
                    "ai_model": "gpt-4"
                },
                "recommended": True
            },
            {
                "id": "business",
                "name": "Business",
                "price": 99,
                "variant_id": settings.LEMONSQUEEZY_BUSINESS_VARIANT_ID,
                "features": [
                    "Everything in Pro",
                    "Team collaboration",
                    "API access",
                    "Custom AI training",
                    "White-label solution",
                    "Dedicated support",
                    "SLA guarantee"
                ],
                "limitations": {
                    "forms_per_month": -1,
                    "data_retention_hours": -1,
                    "ai_model": "gpt-4",
                    "team_members": -1  # Unlimited
                }
            }
        ]
    }

@router.post("/checkout")
async def create_checkout_session(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a LemonSqueezy checkout session"""
    
    if not settings.LEMONSQUEEZY_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Payment system not configured"
        )
    
    # Get the variant ID based on plan
    variant_id = None
    if plan_id == "pro":
        variant_id = settings.LEMONSQUEEZY_PRO_VARIANT_ID
    elif plan_id == "business":
        variant_id = settings.LEMONSQUEEZY_BUSINESS_VARIANT_ID
    else:
        raise HTTPException(status_code=400, detail="Invalid plan ID")
    
    if not variant_id:
        raise HTTPException(
            status_code=503,
            detail="Payment plan not configured"
        )
    
    # Create checkout URL via LemonSqueezy API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.lemonsqueezy.com/v1/checkouts",
            headers={
                "Authorization": f"Bearer {settings.LEMONSQUEEZY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "data": {
                    "type": "checkouts",
                    "attributes": {
                        "variant_id": variant_id,
                        "custom_data": {
                            "user_id": current_user.id,
                            "email": current_user.email
                        }
                    }
                }
            }
        )
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to create checkout session"
            )
        
        checkout_data = response.json()
        checkout_url = checkout_data.get("data", {}).get("attributes", {}).get("url")
        
        return {
            "checkout_url": checkout_url,
            "session_id": checkout_data.get("data", {}).get("id")
        }

@router.get("/subscription")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription status"""
    return {
        "subscription_tier": current_user.subscription_tier or "free",
        "subscription_status": current_user.subscription_status or "inactive",
        "subscription_id": current_user.subscription_id,
        "limits": {
            "forms_per_month": 10 if not current_user.subscription_tier else -1,
            "forms_used": db.query(FormSubmission).filter_by(
                user_id=current_user.id
            ).filter(
                FormSubmission.created_at >= datetime.now().replace(day=1)
            ).count() if current_user.subscription_tier == "free" else 0
        }
    }

@router.post("/cancel-subscription")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    
    if not current_user.subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    # Call LemonSqueezy API to cancel subscription
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://api.lemonsqueezy.com/v1/subscriptions/{current_user.subscription_id}",
            headers={
                "Authorization": f"Bearer {settings.LEMONSQUEEZY_API_KEY}"
            }
        )
        
        if response.status_code == 204:
            current_user.subscription_status = "cancelled"
            db.commit()
            return {"status": "success", "message": "Subscription cancelled"}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to cancel subscription"
            )