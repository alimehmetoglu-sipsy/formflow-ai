from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.subscription import (
    Subscription, SubscriptionStatus, PlanType, Invoice, InvoiceStatus, Usage
)
from app.services.payment import LemonsqueezyService, PlanLimitsService
from app.middleware.usage import UsageTracker
from app.api.dependencies import get_current_user
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/lemonsqueezy")
async def handle_lemonsqueezy_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Lemonsqueezy webhook events"""
    
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("X-Signature")
    
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # Verify signature
    payment_service = LemonsqueezyService()
    if not payment_service.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        data = json.loads(body)
        event_type = data["meta"]["event_name"]
        
        logger.info(f"Received Lemonsqueezy webhook: {event_type}")
        
        # Process event in background
        background_tasks.add_task(
            process_webhook_event,
            event_type,
            data,
            db
        )
        
        return {"status": "success", "event": event_type}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid webhook data: {str(e)}")

async def process_webhook_event(event_type: str, data: Dict, db: Session):
    """Process webhook events in background"""
    
    try:
        if event_type == "subscription_created":
            await handle_subscription_created(data, db)
        elif event_type == "subscription_updated":
            await handle_subscription_updated(data, db)
        elif event_type == "subscription_cancelled":
            await handle_subscription_cancelled(data, db)
        elif event_type == "subscription_resumed":
            await handle_subscription_resumed(data, db)
        elif event_type == "subscription_expired":
            await handle_subscription_expired(data, db)
        elif event_type == "subscription_payment_success":
            await handle_payment_success(data, db)
        elif event_type == "subscription_payment_failed":
            await handle_payment_failed(data, db)
        elif event_type == "order_created":
            await handle_order_created(data, db)
        else:
            logger.info(f"Unhandled webhook event: {event_type}")
            
    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {e}")

async def handle_subscription_created(data: Dict, db: Session):
    """Handle new subscription creation"""
    
    attributes = data["data"]["attributes"]
    custom_data = attributes.get("custom_data", {})
    user_id = custom_data.get("user_id")
    
    if not user_id:
        logger.error("No user_id in subscription_created webhook")
        return
    
    # Get user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        logger.error(f"User {user_id} not found for subscription creation")
        return
    
    # Determine plan type from variant
    variant_id = str(attributes["variant_id"])
    plan_type = PlanType.FREE
    
    if variant_id == settings.LEMONSQUEEZY_PRO_VARIANT_ID:
        plan_type = PlanType.PRO
    elif variant_id == settings.LEMONSQUEEZY_BUSINESS_VARIANT_ID:
        plan_type = PlanType.BUSINESS
    
    # Create subscription record
    subscription = Subscription(
        user_id=user_id,
        lemonsqueezy_subscription_id=str(data["data"]["id"]),
        lemonsqueezy_order_id=str(attributes.get("order_id", "")),
        lemonsqueezy_product_id=str(attributes.get("product_id", "")),
        lemonsqueezy_variant_id=variant_id,
        plan_type=plan_type,
        plan_name=attributes.get("product_name", plan_type.value.title()),
        status=SubscriptionStatus(attributes["status"]),
        current_period_start=datetime.fromisoformat(attributes["renews_at"].replace("Z", "+00:00")),
        current_period_end=datetime.fromisoformat(attributes["renews_at"].replace("Z", "+00:00")),
        trial_end=datetime.fromisoformat(attributes["trial_ends_at"].replace("Z", "+00:00")) if attributes.get("trial_ends_at") else None,
        unit_price=int(float(attributes["unit_price"]) * 100),  # Convert to cents
        currency=attributes.get("currency", "USD")
    )
    
    db.add(subscription)
    
    # Update user plan
    user.plan_type = plan_type
    
    db.commit()
    
    logger.info(f"Created subscription {subscription.id} for user {user_id} with plan {plan_type.value}")

async def handle_subscription_updated(data: Dict, db: Session):
    """Handle subscription updates"""
    
    subscription_id = str(data["data"]["id"])
    attributes = data["data"]["attributes"]
    
    subscription = db.query(Subscription).filter_by(
        lemonsqueezy_subscription_id=subscription_id
    ).first()
    
    if not subscription:
        logger.error(f"Subscription {subscription_id} not found for update")
        return
    
    # Update subscription
    subscription.status = SubscriptionStatus(attributes["status"])
    subscription.current_period_end = datetime.fromisoformat(attributes["renews_at"].replace("Z", "+00:00"))
    
    if attributes.get("ends_at"):
        subscription.cancel_at = datetime.fromisoformat(attributes["ends_at"].replace("Z", "+00:00"))
    
    db.commit()
    
    logger.info(f"Updated subscription {subscription_id} with status {attributes['status']}")

async def handle_subscription_cancelled(data: Dict, db: Session):
    """Handle subscription cancellation"""
    
    subscription_id = str(data["data"]["id"])
    attributes = data["data"]["attributes"]
    
    subscription = db.query(Subscription).filter_by(
        lemonsqueezy_subscription_id=subscription_id
    ).first()
    
    if subscription:
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        if attributes.get("ends_at"):
            subscription.cancel_at = datetime.fromisoformat(attributes["ends_at"].replace("Z", "+00:00"))
        
        # Don't immediately downgrade - wait until period ends
        db.commit()
        
        logger.info(f"Cancelled subscription {subscription_id}")

async def handle_payment_success(data: Dict, db: Session):
    """Handle successful payment"""
    
    attributes = data["data"]["attributes"]
    subscription_id = str(attributes.get("subscription_id"))
    
    if subscription_id:
        subscription = db.query(Subscription).filter_by(
            lemonsqueezy_subscription_id=subscription_id
        ).first()
        
        if subscription and subscription.status != SubscriptionStatus.ACTIVE:
            subscription.status = SubscriptionStatus.ACTIVE
            db.commit()
            
            logger.info(f"Subscription {subscription_id} reactivated after successful payment")

async def handle_payment_failed(data: Dict, db: Session):
    """Handle failed payment"""
    
    attributes = data["data"]["attributes"]
    subscription_id = str(attributes.get("subscription_id"))
    
    if subscription_id:
        subscription = db.query(Subscription).filter_by(
            lemonsqueezy_subscription_id=subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            db.commit()
            
            logger.warning(f"Subscription {subscription_id} marked as past due after failed payment")

@router.get("/dashboard")
async def get_billing_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's billing dashboard information"""
    
    # Get active subscription
    subscription = db.query(Subscription).filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    # Get usage information
    usage_summary = UsageTracker.get_usage_summary(current_user.id, db)
    
    # Get recent invoices
    invoices = db.query(Invoice).filter_by(
        user_id=current_user.id
    ).order_by(Invoice.created_at.desc()).limit(5).all()
    
    # Get plan limits
    limits = PlanLimitsService.get_plan_limits(current_user.plan_type.value)
    
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "plan": current_user.plan_type.value
        },
        "subscription": {
            "id": subscription.id if subscription else None,
            "plan": subscription.plan_type.value if subscription else current_user.plan_type.value,
            "status": subscription.status.value if subscription else "none",
            "current_period_start": subscription.current_period_start if subscription else None,
            "current_period_end": subscription.current_period_end if subscription else None,
            "cancel_at": subscription.cancel_at if subscription else None,
            "cancelled_at": subscription.cancelled_at if subscription else None,
            "trial_end": subscription.trial_end if subscription else None,
            "unit_price": subscription.unit_price / 100 if subscription else 0,
            "currency": subscription.currency if subscription else "USD"
        },
        "usage": usage_summary,
        "invoices": [
            {
                "id": inv.id,
                "amount": inv.amount_total / 100,
                "currency": inv.currency,
                "status": inv.status.value,
                "invoice_date": inv.invoice_date,
                "due_date": inv.due_date,
                "paid_at": inv.paid_at,
                "invoice_url": inv.invoice_url,
                "pdf_url": inv.pdf_url
            }
            for inv in invoices
        ],
        "features": limits
    }

@router.post("/checkout")
async def create_checkout(
    plan: str,
    current_user: User = Depends(get_current_user)
):
    """Create checkout session for plan upgrade"""
    
    # Map plans to variant IDs
    variant_ids = {
        "pro": settings.LEMONSQUEEZY_PRO_VARIANT_ID,
        "business": settings.LEMONSQUEEZY_BUSINESS_VARIANT_ID
    }
    
    if plan.lower() not in variant_ids:
        raise HTTPException(
            status_code=400, 
            detail="Invalid plan. Choose 'pro' or 'business'"
        )
    
    # Check if user already has this plan or higher
    current_plan_hierarchy = {"free": 0, "pro": 1, "business": 2}
    current_level = current_plan_hierarchy.get(current_user.plan_type.value, 0)
    target_level = current_plan_hierarchy.get(plan.lower(), 0)
    
    if current_level >= target_level:
        raise HTTPException(
            status_code=400,
            detail=f"You already have {current_user.plan_type.value} plan or higher"
        )
    
    try:
        payment_service = LemonsqueezyService()
        checkout_url = await payment_service.create_checkout(
            variant_id=variant_ids[plan.lower()],
            user_email=current_user.email,
            user_id=current_user.id,
            custom_data={
                "upgrade_from": current_user.plan_type.value,
                "user_name": current_user.full_name or current_user.email
            }
        )
        
        return {
            "checkout_url": checkout_url,
            "plan": plan.lower(),
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Failed to create checkout for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create checkout session. Please try again."
        )

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel user's subscription"""
    
    subscription = db.query(Subscription).filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404, 
            detail="No active subscription found"
        )
    
    try:
        payment_service = LemonsqueezyService()
        success = await payment_service.cancel_subscription(
            subscription.lemonsqueezy_subscription_id
        )
        
        if success:
            return {
                "message": f"Subscription will be cancelled at the end of your current period ({subscription.current_period_end.date()})",
                "cancel_at": subscription.current_period_end,
                "access_until": subscription.current_period_end
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to cancel subscription. Please contact support."
            )
            
    except Exception as e:
        logger.error(f"Failed to cancel subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel subscription. Please try again or contact support."
        )

@router.get("/usage")
async def get_usage_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed usage information"""
    
    return UsageTracker.get_usage_summary(current_user.id, db)

@router.get("/customer-portal")
async def get_customer_portal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get customer portal URL for subscription management"""
    
    subscription = db.query(Subscription).filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="No active subscription found"
        )
    
    try:
        payment_service = LemonsqueezyService()
        portal_url = await payment_service.create_customer_portal(
            subscription.lemonsqueezy_subscription_id
        )
        
        if portal_url:
            return {"portal_url": portal_url}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create customer portal"
            )
            
    except Exception as e:
        logger.error(f"Failed to create customer portal for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create customer portal. Please try again."
        )