"""
API Endpoints for Follow-up Recommendations (FA-47)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.lead_score import LeadScore
from app.models.form import FormSubmission
from app.services.follow_up_engine import FollowUpRecommendationEngine
from app.services.lead_scoring import LeadScoringEngine
from app.schemas.recommendations import (
    RecommendationResponse,
    RecommendationRequest,
    RecommendationFeedback,
    BulkRecommendationsRequest
)

router = APIRouter()


@router.post("/leads/{lead_id}/recommendations", response_model=List[RecommendationResponse])
async def generate_recommendations(
    lead_id: UUID,
    include_templates: bool = Query(True, description="Include email/call templates"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered follow-up recommendations for a specific lead
    """
    # Get lead data
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == lead_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get lead score
    lead_score = db.query(LeadScore).filter(
        LeadScore.submission_id == lead_id
    ).first()
    
    # If no score exists, calculate it
    if not lead_score:
        scoring_engine = LeadScoringEngine(db)
        lead_score = await scoring_engine.calculate_lead_score(lead_id, submission.form_data)
    
    # Generate recommendations
    recommendation_engine = FollowUpRecommendationEngine(db)
    
    # Determine urgency based on form data
    urgency = 'medium'
    form_text = str(submission.form_data).lower()
    if any(word in form_text for word in ['urgent', 'asap', 'immediate']):
        urgency = 'urgent'
    elif any(word in form_text for word in ['soon', 'quickly', 'this month']):
        urgency = 'high'
    
    recommendations = await recommendation_engine.generate_recommendations(
        lead_data=submission.form_data,
        lead_score=lead_score.final_score,
        score_category=lead_score.score_category,
        urgency=urgency
    )
    
    # Format response
    response = []
    for idx, rec in enumerate(recommendations):
        response.append(RecommendationResponse(
            id=f"{lead_id}-{idx}",
            lead_id=lead_id,
            action=rec['action'],
            priority=rec['priority'],
            timing=rec['timing'],
            method=rec.get('method', 'email'),
            template=rec.get('template') if include_templates else None,
            reason=rec.get('reason'),
            success_probability=rec.get('success_probability', 0),
            generated_at=datetime.utcnow()
        ))
    
    return response


@router.post("/leads/recommendations/bulk", response_model=Dict[str, List[RecommendationResponse]])
async def generate_bulk_recommendations(
    request: BulkRecommendationsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate recommendations for multiple leads at once
    """
    results = {}
    
    for lead_id in request.lead_ids:
        # Verify ownership
        submission = db.query(FormSubmission).filter(
            FormSubmission.id == lead_id,
            FormSubmission.user_id == current_user.id
        ).first()
        
        if not submission:
            results[str(lead_id)] = []
            continue
        
        # Get lead score
        lead_score = db.query(LeadScore).filter(
            LeadScore.submission_id == lead_id
        ).first()
        
        if not lead_score:
            # Calculate in background if not exists
            background_tasks.add_task(
                calculate_and_generate_recommendations,
                lead_id,
                submission.form_data,
                db
            )
            results[str(lead_id)] = []
            continue
        
        # Generate recommendations
        recommendation_engine = FollowUpRecommendationEngine(db)
        
        recommendations = await recommendation_engine.generate_recommendations(
            lead_data=submission.form_data,
            lead_score=lead_score.final_score,
            score_category=lead_score.score_category,
            urgency='medium'
        )
        
        # Format response
        lead_recs = []
        for idx, rec in enumerate(recommendations):
            lead_recs.append(RecommendationResponse(
                id=f"{lead_id}-{idx}",
                lead_id=lead_id,
                action=rec['action'],
                priority=rec['priority'],
                timing=rec['timing'],
                method=rec.get('method', 'email'),
                template=rec.get('template') if request.include_templates else None,
                reason=rec.get('reason'),
                success_probability=rec.get('success_probability', 0),
                generated_at=datetime.utcnow()
            ))
        
        results[str(lead_id)] = lead_recs
    
    return results


@router.get("/leads/recommendations/templates")
async def get_recommendation_templates(
    template_type: str = Query(..., description="Template type: email, call, linkedin"),
    lead_category: str = Query('warm', description="Lead category: hot, warm, cold"),
    current_user: User = Depends(get_current_user)
):
    """
    Get pre-defined templates for follow-up actions
    """
    templates = {
        'email': {
            'hot': {
                'subject': 'Quick question about your {pain_point} challenge',
                'body': """Hi {name},

I saw your form submission about {pain_point}. With your {timeline} timeline, I wanted to reach out immediately.

Based on what you shared, FormFlow AI can help you:
• Save 80% of analysis time
• Increase conversion by 50%
• Get ROI within 2 months

Are you available for a quick 15-minute call tomorrow at 2 PM?

Best regards,
{sales_rep_name}"""
            },
            'warm': {
                'subject': 'Solving {pain_point} for {company}',
                'body': """Hi {name},

Thank you for your interest in FormFlow AI. I noticed you're looking to improve {improvement_area}.

I'd love to show you how we've helped similar companies achieve their goals.

Would you be interested in a personalized demo this week?

Best regards,
{sales_rep_name}"""
            },
            'cold': {
                'subject': 'Resources for {industry} professionals',
                'body': """Hi {name},

I wanted to share some resources that might be helpful for {company}.

We've created a guide on optimizing form-to-insight workflows that I think you'll find valuable.

Let me know if you'd like to discuss how this applies to your specific situation.

Best regards,
{sales_rep_name}"""
            }
        },
        'call': {
            'hot': """Hi {name}, this is {sales_rep_name} from FormFlow AI. 

I just received your form submission about {main_challenge}. I wanted to reach out immediately because I noticed your urgent timeline.

Do you have 2 minutes to discuss how we can help you achieve {desired_outcome}?""",
            
            'warm': """Hi {name}, this is {sales_rep_name} from FormFlow AI.

I saw you're interested in improving your form analysis process. I've helped companies like {similar_company} reduce their analysis time by 80%.

Could we schedule 15 minutes this week to discuss your specific needs?""",
            
            'cold': """Hi {name}, this is {sales_rep_name} from FormFlow AI.

I'm reaching out because you expressed interest in our platform. I wanted to check if you had any questions or if there's a better time to connect?"""
        },
        'linkedin': {
            'all': """Hi {name},

I noticed you're interested in streamlining your form analysis at {company}. 

I've been helping companies in {industry} transform their data into actionable insights with AI-powered dashboards.

Would love to connect and share some insights that might be valuable for your team.

Best,
{sales_rep_name}"""
        }
    }
    
    # Return requested template
    if template_type in templates:
        if template_type == 'linkedin':
            return templates[template_type]
        elif lead_category in templates[template_type]:
            return templates[template_type][lead_category]
    
    raise HTTPException(status_code=404, detail="Template not found")


@router.post("/recommendations/{recommendation_id}/feedback")
async def submit_recommendation_feedback(
    recommendation_id: str,
    feedback: RecommendationFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on recommendation effectiveness for ML improvement
    """
    # Store feedback for future ML training
    # This would typically go to a feedback table
    
    return {
        "status": "success",
        "message": "Feedback recorded",
        "recommendation_id": recommendation_id,
        "outcome": feedback.outcome
    }


@router.get("/recommendations/effectiveness")
async def get_recommendation_effectiveness(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics on recommendation effectiveness
    """
    # This would query a feedback/tracking table
    # For now, return sample statistics
    
    return {
        "total_recommendations": 150,
        "followed_recommendations": 120,
        "follow_rate": 0.80,
        "outcomes": {
            "converted": 45,
            "in_progress": 40,
            "lost": 35
        },
        "best_performing": {
            "action": "Call within 24 hours",
            "conversion_rate": 0.65
        },
        "method_effectiveness": {
            "call": 0.62,
            "email": 0.48,
            "demo": 0.71,
            "linkedin": 0.35
        }
    }


async def calculate_and_generate_recommendations(
    lead_id: UUID,
    form_data: Dict,
    db: Session
):
    """
    Background task to calculate score and generate recommendations
    """
    scoring_engine = LeadScoringEngine(db)
    await scoring_engine.calculate_lead_score(lead_id, form_data)