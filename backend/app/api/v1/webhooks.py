from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends, status, Query
from sqlalchemy.orm import Session
from app.schemas.webhook import TypeformWebhook
from app.schemas.google_forms import GoogleFormsWebhook
from app.schemas.custom_webhook import (
    WebhookConfigCreate, WebhookConfigUpdate, WebhookConfigResponse,
    WebhookLogResponse, CustomWebhookPayload, WebhookTestRequest,
    WebhookTestResponse, PLATFORM_PRESETS
)
from app.models.form import FormSubmission, Dashboard
from app.models.webhook import WebhookConfig, WebhookLog
from app.models.user import User
from app.database import get_db
from app.config import settings
from app.services.ai_processor import AIProcessor
from app.services.template_engine import TemplateEngine
from app.services.custom_webhook_processor import CustomWebhookProcessor
from app.api.v1.auth import get_current_user
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

router = APIRouter()

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Typeform webhook signature"""
    if not secret:
        return True  # Skip verification if no secret configured
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@router.post("/typeform")
async def receive_typeform_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Receive and process Typeform webhook"""
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature if secret is configured
    if settings.TYPEFORM_WEBHOOK_SECRET:
        signature = request.headers.get("Typeform-Signature")
        if not signature or not verify_signature(body, signature, settings.TYPEFORM_WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    try:
        data = json.loads(body)
        webhook = TypeformWebhook(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook data: {str(e)}")
    
    # Extract form information
    form_response = webhook.form_response
    response_id = form_response.get("token", "")
    
    # Check if submission already exists
    existing = db.query(FormSubmission).filter_by(response_id=response_id).first()
    if existing:
        return {
            "status": "already_processed",
            "dashboard_url": f"{settings.FRONTEND_URL}{existing.dashboard_url}",
            "submission_id": existing.id
        }
    
    # Store submission
    submission = FormSubmission(
        user_id=user_id,  # Associate with user if provided
        typeform_id=form_response.get("form_id", ""),
        form_title=form_response.get("definition", {}).get("title", "Untitled Form"),
        response_id=response_id,
        submitted_at=datetime.fromisoformat(form_response.get("submitted_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")),
        answers=webhook.parse_answers(),
        dashboard_url=f"/dashboard/{response_id}"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Trigger AI processing in background
    background_tasks.add_task(
        process_submission,
        submission_id=submission.id,
        answers=submission.answers
    )
    
    return {
        "status": "success",
        "dashboard_url": f"{settings.FRONTEND_URL}{submission.dashboard_url}",
        "submission_id": submission.id,
        "message": "Form submission received and processing started"
    }

def process_submission(submission_id: str, answers: Dict[str, Any]):
    """Background task to process submission with AI"""
    import asyncio
    from app.database import SessionLocal
    
    # Run the async processing in a new event loop
    asyncio.run(_process_submission_async(submission_id, answers))

async def _process_submission_async(submission_id: str, answers: Dict[str, Any]):
    """Async helper for processing submission"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Determine template type based on form content
        template_type = detect_template_type(answers)
        
        # Process with AI
        ai_processor = AIProcessor()
        ai_content = await ai_processor.process(answers, template_type)
        
        # Generate HTML dashboard
        template_engine = TemplateEngine()
        html_content = template_engine.render(template_type, ai_content)
        
        # Store dashboard
        dashboard = Dashboard(
            submission_id=submission_id,
            template_type=template_type,
            ai_generated_content=ai_content,
            html_content=html_content
        )
        db.add(dashboard)
        
        # Mark submission as processed
        submission = db.query(FormSubmission).filter_by(id=submission_id).first()
        if submission:
            submission.processed = True
        
        db.commit()
        print(f"✅ Successfully processed submission {submission_id}")
        
    except Exception as e:
        print(f"❌ Error processing submission {submission_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()

def detect_template_type(answers: Dict[str, Any]) -> str:
    """Detect which template to use based on form answers"""
    # Combine all answer values into a single text for analysis
    text = " ".join(str(v).lower() for v in answers.values() if v)
    
    # Keywords for different template types
    diet_keywords = ["diet", "weight", "calories", "meal", "nutrition", "food", "eating", "healthy"]
    lead_keywords = ["lead", "company", "budget", "timeline", "business", "purchase", "decision"]
    event_keywords = ["event", "registration", "attend", "ticket", "conference", "workshop"]
    
    # Count keyword matches
    diet_score = sum(1 for keyword in diet_keywords if keyword in text)
    lead_score = sum(1 for keyword in lead_keywords if keyword in text)
    event_score = sum(1 for keyword in event_keywords if keyword in text)
    
    # Return template with highest score
    scores = {
        "diet_plan": diet_score,
        "lead_score": lead_score,
        "event_registration": event_score
    }
    
    template = max(scores, key=scores.get)
    
    # Default to generic if no clear match
    if scores[template] == 0:
        return "generic"
    
    return template

@router.post("/google-forms")
async def receive_google_forms_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Receive and process Google Forms webhook"""
    
    # Get raw body
    body = await request.body()
    
    # Parse webhook data
    try:
        data = json.loads(body)
        print(f"📥 Google Forms webhook received: {json.dumps(data, indent=2)}")
        
        # If data is empty or missing required fields, log it
        if not data:
            print("❌ Empty webhook data received")
            raise ValueError("Empty webhook data")
            
        google_webhook = GoogleFormsWebhook(**data)
        
        # Convert to Typeform format for compatibility
        typeform_data = google_webhook.to_typeform_format()
        webhook = TypeformWebhook(**typeform_data)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        print(f"Body received: {body}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Webhook processing error: {str(e)}")
        print(f"Data received: {data if 'data' in locals() else 'No data'}")
        raise HTTPException(status_code=400, detail=f"Invalid webhook data: {str(e)}")
    
    # Extract form information
    form_response = webhook.form_response
    response_id = form_response.get("token", "")
    
    # For Google Forms, always create a new submission
    # Add timestamp to make it unique
    import uuid
    unique_id = f"{response_id}_{uuid.uuid4().hex[:8]}"
    
    # Skip duplicate check for Google Forms - always create new dashboard
    # This allows the same form to be submitted multiple times
    print(f"Creating new submission with unique ID: {unique_id}")
    
    # Store submission with unique ID
    submission = FormSubmission(
        user_id=user_id,  # Associate with user if provided
        typeform_id=form_response.get("form_id", ""),
        form_title=form_response.get("definition", {}).get("title", "Untitled Form"),
        response_id=unique_id,  # Use unique ID to allow multiple submissions
        submitted_at=datetime.fromisoformat(form_response.get("submitted_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")),
        answers=webhook.parse_answers(),
        dashboard_url=f"/dashboard/{unique_id}"  # Use unique ID in dashboard URL
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Trigger AI processing in background
    background_tasks.add_task(
        process_submission,
        submission_id=submission.id,
        answers=submission.answers
    )
    
    return {
        "status": "success",
        "dashboard_url": f"{settings.FRONTEND_URL}{submission.dashboard_url}",
        "submission_id": submission.id,
        "message": "Google Forms submission received and processing started",
        "source": "google_forms"
    }

# Custom Webhook Management Endpoints

@router.get("/configs", response_model=List[WebhookConfigResponse])
async def list_webhook_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all webhook configurations for the current user"""
    configs = db.query(WebhookConfig).filter(WebhookConfig.user_id == current_user.id).all()
    
    # Add webhook URL to each config
    response_configs = []
    for config in configs:
        config_dict = config.to_dict()
        config_dict["webhook_url"] = f"{settings.BACKEND_URL}/api/v1/webhooks/custom/{config.webhook_token}"
        response_configs.append(WebhookConfigResponse(**config_dict))
    
    return response_configs

@router.post("/configs", response_model=WebhookConfigResponse)
async def create_webhook_config(
    config_data: WebhookConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webhook configuration"""
    
    # Apply platform preset if specified
    field_mappings = config_data.field_mappings
    if config_data.platform in PLATFORM_PRESETS and not field_mappings:
        field_mappings = PLATFORM_PRESETS[config_data.platform]
    
    config = WebhookConfig(
        user_id=current_user.id,
        name=config_data.name,
        platform=config_data.platform,
        field_mappings=field_mappings,
        signature_secret=config_data.signature_secret,
        is_active=config_data.is_active
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    # Add webhook URL
    config_dict = config.to_dict()
    config_dict["webhook_url"] = f"{settings.BACKEND_URL}/api/v1/webhooks/custom/{config.webhook_token}"
    
    return WebhookConfigResponse(**config_dict)

@router.put("/configs/{config_id}", response_model=WebhookConfigResponse)
async def update_webhook_config(
    config_id: str,
    config_data: WebhookConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a webhook configuration"""
    config = db.query(WebhookConfig).filter(
        WebhookConfig.id == config_id,
        WebhookConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Webhook configuration not found")
    
    # Update fields
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    # Add webhook URL
    config_dict = config.to_dict()
    config_dict["webhook_url"] = f"{settings.BACKEND_URL}/api/v1/webhooks/custom/{config.webhook_token}"
    
    return WebhookConfigResponse(**config_dict)

@router.delete("/configs/{config_id}")
async def delete_webhook_config(
    config_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a webhook configuration"""
    config = db.query(WebhookConfig).filter(
        WebhookConfig.id == config_id,
        WebhookConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Webhook configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "Webhook configuration deleted successfully"}

@router.get("/configs/{config_id}/logs", response_model=List[WebhookLogResponse])
async def get_webhook_logs(
    config_id: str,
    limit: int = Query(default=10, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get webhook logs for a configuration"""
    config = db.query(WebhookConfig).filter(
        WebhookConfig.id == config_id,
        WebhookConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Webhook configuration not found")
    
    logs = db.query(WebhookLog).filter(
        WebhookLog.webhook_config_id == config_id
    ).order_by(WebhookLog.created_at.desc()).limit(limit).all()
    
    return [WebhookLogResponse(**log.to_dict()) for log in logs]

@router.post("/test", response_model=WebhookTestResponse)
async def test_webhook_config(
    test_request: WebhookTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test a webhook configuration with sample data"""
    config = db.query(WebhookConfig).filter(
        WebhookConfig.id == test_request.webhook_config_id,
        WebhookConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Webhook configuration not found")
    
    processor = CustomWebhookProcessor(db)
    result = processor.test_mapping(config, test_request.test_data)
    
    return WebhookTestResponse(**result)

@router.get("/presets")
async def get_platform_presets():
    """Get available platform presets for field mappings"""
    return {
        "presets": PLATFORM_PRESETS,
        "platforms": list(PLATFORM_PRESETS.keys())
    }

# Custom Webhook Receiver Endpoint

@router.post("/custom/{webhook_token}")
async def receive_custom_webhook(
    webhook_token: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Receive and process custom webhook"""
    
    # Find webhook configuration
    config = db.query(WebhookConfig).filter(
        WebhookConfig.webhook_token == webhook_token,
        WebhookConfig.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")
    
    # Get raw body and headers
    body = await request.body()
    headers = dict(request.headers)
    
    # Get client IP
    client_host = request.client.host if request.client else None
    
    # Verify signature if configured
    if config.signature_secret:
        signature = headers.get("x-signature") or headers.get("x-hub-signature-256") or headers.get("signature")
        if signature:
            processor = CustomWebhookProcessor(db)
            if not processor.verify_signature(body, signature, config.signature_secret, config.platform):
                raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON body
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Process webhook in background
    background_tasks.add_task(
        process_custom_webhook,
        config_id=config.id,
        data=data,
        ip_address=client_host
    )
    
    return {
        "status": "success",
        "message": "Custom webhook received and processing started"
    }

async def process_custom_webhook(config_id: str, data: Dict[str, Any], ip_address: Optional[str]):
    """Background task to process custom webhook"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Get webhook config
        config = db.query(WebhookConfig).filter(WebhookConfig.id == config_id).first()
        if not config:
            return
        
        # Process with custom webhook processor
        processor = CustomWebhookProcessor(db)
        result = await processor.process(config, data, ip_address)
        
        # Trigger AI processing
        if result.get("status") == "success":
            submission_id = result.get("submission_id")
            if submission_id:
                submission = db.query(FormSubmission).filter(FormSubmission.id == submission_id).first()
                if submission:
                    # Process submission
                    background_process_submission(submission.id, submission.answers)
        
        print(f"✅ Successfully processed custom webhook: {result}")
        
    except Exception as e:
        print(f"❌ Error processing custom webhook: {str(e)}")
    finally:
        db.close()

def background_process_submission(submission_id: str, answers: Dict[str, Any]):
    """Process submission with AI (same as existing function)"""
    import asyncio
    asyncio.run(_process_submission_async(submission_id, answers))

@router.get("/test")
async def test_webhook_endpoint():
    """Test endpoint to verify webhook is accessible"""
    return {
        "status": "ok",
        "message": "Webhook endpoint is working",
        "typeform_url": f"{settings.BACKEND_URL}/api/v1/webhooks/typeform",
        "google_forms_url": f"{settings.BACKEND_URL}/api/v1/webhooks/google-forms",
        "custom_webhook_url": f"{settings.BACKEND_URL}/api/v1/webhooks/custom/{{webhook_token}}"
    }