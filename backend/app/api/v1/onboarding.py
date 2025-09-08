from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import httpx
import logging

from app.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class TypeformConnection(BaseModel):
    api_key: str

class TemplateSelection(BaseModel):
    template_id: str
    form_name: Optional[str] = None

class OnboardingStatus(BaseModel):
    step: str
    completed: bool
    data: Optional[dict] = None

# Background tasks
async def send_welcome_email(email: str, full_name: Optional[str] = None):
    """Send welcome email after onboarding completion"""
    logger.info(f"Welcome email would be sent to {email}")
    # In production: integrate with email service

async def import_typeform_forms(user_id: str, api_key: str):
    """Import existing Typeform forms for user"""
    logger.info(f"Would import Typeform forms for user {user_id}")
    # In production: integrate with Typeform API to import existing forms

# Onboarding endpoints
@router.get("/onboarding/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user)
):
    """Get current onboarding status"""
    
    steps = {
        "profile": {
            "completed": bool(current_user.full_name),
            "required": True
        },
        "typeform_connection": {
            "completed": current_user.typeform_connected,
            "required": False
        },
        "template_selection": {
            "completed": False,  # Could check if user has created any forms
            "required": False
        },
        "first_form": {
            "completed": False,  # Could check if user has created any forms
            "required": False
        }
    }
    
    overall_progress = sum(1 for step in steps.values() if step["completed"]) / len(steps)
    
    return {
        "user_id": current_user.id,
        "onboarding_completed": current_user.onboarding_completed,
        "progress": overall_progress,
        "steps": steps,
        "next_step": _get_next_step(steps)
    }

def _get_next_step(steps: dict) -> Optional[str]:
    """Determine the next onboarding step"""
    for step_name, step_data in steps.items():
        if not step_data["completed"]:
            return step_name
    return None

@router.post("/onboarding/typeform-connect")
async def connect_typeform(
    connection_data: TypeformConnection,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect Typeform account"""
    
    # Validate Typeform API key
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.typeform.com/me",
                headers={"Authorization": f"Bearer {connection_data.api_key}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Typeform API key"
                )
            
            typeform_user = response.json()
            logger.info(f"Typeform connection validated for user: {typeform_user.get('alias', 'unknown')}")
            
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Typeform API request timed out"
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to Typeform API"
            )
    
    # Save API key (in production, encrypt this)
    current_user.typeform_api_key = connection_data.api_key
    current_user.typeform_connected = True
    db.commit()
    
    # Import existing forms in background
    background_tasks.add_task(import_typeform_forms, current_user.id, connection_data.api_key)
    
    return {
        "message": "Typeform connected successfully",
        "typeform_user": typeform_user.get('alias', 'Connected User')
    }

@router.post("/onboarding/select-template")
async def select_template(
    template_data: TemplateSelection,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Select initial template and create sample form"""
    
    # Validate template ID
    available_templates = [
        "diet_plan",
        "lead_score", 
        "event_registration",
        "customer_feedback",
        "job_application",
        "product_survey"
    ]
    
    if template_data.template_id not in available_templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template. Available templates: {', '.join(available_templates)}"
        )
    
    # In a full implementation, you would create a sample form here
    # For now, we'll just track the selection
    
    form_name = template_data.form_name or f"Sample {template_data.template_id.replace('_', ' ').title()} Form"
    
    logger.info(f"User {current_user.id} selected template {template_data.template_id}")
    
    return {
        "message": "Template selected successfully",
        "template_id": template_data.template_id,
        "form_name": form_name,
        "next_step": "Create your first form using this template"
    }

@router.post("/onboarding/skip-step")
async def skip_onboarding_step(
    step_data: OnboardingStatus,
    current_user: User = Depends(get_current_user)
):
    """Skip an optional onboarding step"""
    
    optional_steps = ["typeform_connection", "template_selection", "first_form"]
    
    if step_data.step not in optional_steps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot skip required onboarding steps"
        )
    
    logger.info(f"User {current_user.id} skipped onboarding step: {step_data.step}")
    
    return {
        "message": f"Skipped {step_data.step}",
        "step": step_data.step,
        "skipped": True
    }

@router.post("/onboarding/complete")
async def complete_onboarding(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark onboarding as complete"""
    
    # Check if required steps are completed
    if not current_user.full_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile before finishing onboarding"
        )
    
    # Mark onboarding as completed
    current_user.onboarding_completed = True
    db.commit()
    
    # Send welcome email
    background_tasks.add_task(
        send_welcome_email, 
        current_user.email, 
        current_user.full_name
    )
    
    logger.info(f"User {current_user.id} completed onboarding")
    
    return {
        "message": "Welcome to FormFlow AI! 🎉",
        "onboarding_completed": True,
        "next_steps": [
            "Create your first form",
            "Set up webhooks", 
            "Explore AI-powered dashboards"
        ]
    }

@router.post("/onboarding/restart")
async def restart_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart onboarding process"""
    
    current_user.onboarding_completed = False
    db.commit()
    
    logger.info(f"User {current_user.id} restarted onboarding")
    
    return {
        "message": "Onboarding process restarted",
        "onboarding_completed": False
    }

# Helper endpoints
@router.get("/onboarding/templates")
async def get_available_templates():
    """Get list of available form templates"""
    
    templates = [
        {
            "id": "diet_plan",
            "name": "Diet Plan Generator",
            "description": "Generate personalized diet plans from health questionnaires",
            "category": "Health & Fitness",
            "preview_url": "/templates/diet_plan/preview"
        },
        {
            "id": "lead_score", 
            "name": "Lead Scoring Dashboard",
            "description": "Score and prioritize leads from contact forms",
            "category": "Sales & Marketing",
            "preview_url": "/templates/lead_score/preview"
        },
        {
            "id": "event_registration",
            "name": "Event Registration",
            "description": "Manage event registrations with attendee insights",
            "category": "Events",
            "preview_url": "/templates/event_registration/preview"
        },
        {
            "id": "customer_feedback",
            "name": "Customer Feedback Analysis",
            "description": "Analyze customer feedback and satisfaction scores",
            "category": "Customer Service",
            "preview_url": "/templates/customer_feedback/preview"
        },
        {
            "id": "job_application",
            "name": "Job Application Screening",
            "description": "Screen job applications and rank candidates",
            "category": "HR & Recruitment",
            "preview_url": "/templates/job_application/preview"
        },
        {
            "id": "product_survey",
            "name": "Product Survey Dashboard", 
            "description": "Analyze product feedback and feature requests",
            "category": "Product Management",
            "preview_url": "/templates/product_survey/preview"
        }
    ]
    
    return {
        "templates": templates,
        "total": len(templates)
    }

@router.get("/onboarding/typeform-status")
async def check_typeform_status(
    current_user: User = Depends(get_current_user)
):
    """Check Typeform connection status"""
    
    if not current_user.typeform_connected:
        return {
            "connected": False,
            "message": "Typeform not connected"
        }
    
    # In production, verify the API key is still valid
    return {
        "connected": True,
        "message": "Typeform connected successfully",
        "api_key_valid": True  # Would check this in production
    }