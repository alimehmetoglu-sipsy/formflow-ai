"""
API Endpoints for Lead Scoring (FA-45)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.lead_score import LeadScore
from app.models.form import FormSubmission
from app.services.lead_scoring import LeadScoringEngine
from app.schemas.lead_score import (
    LeadScoreResponse,
    LeadScoreCreate,
    LeadScoreExplanation,
    ScoringRuleCreate,
    ScoringRuleResponse
)

router = APIRouter()


@router.post("/submissions/{submission_id}/score", response_model=LeadScoreResponse)
async def calculate_lead_score(
    submission_id: UUID,
    force_recalculate: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate or retrieve lead score for a form submission
    """
    # Check if submission exists and belongs to user
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if score already exists
    existing_score = db.query(LeadScore).filter(
        LeadScore.submission_id == submission_id
    ).first()
    
    if existing_score and not force_recalculate:
        return existing_score
    
    # Calculate new score
    scoring_engine = LeadScoringEngine(db)
    lead_score = await scoring_engine.calculate_lead_score(
        submission_id,
        submission.form_data
    )
    
    return lead_score


@router.get("/submissions/{submission_id}/score", response_model=LeadScoreResponse)
async def get_lead_score(
    submission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get existing lead score for a submission
    """
    # Verify ownership
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    lead_score = db.query(LeadScore).filter(
        LeadScore.submission_id == submission_id
    ).first()
    
    if not lead_score:
        raise HTTPException(status_code=404, detail="Lead score not found")
    
    return lead_score


@router.get("/submissions/{submission_id}/score/explanation", response_model=LeadScoreExplanation)
async def get_score_explanation(
    submission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation of how the lead score was calculated
    """
    # Verify ownership
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == submission_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    lead_score = db.query(LeadScore).filter(
        LeadScore.submission_id == submission_id
    ).first()
    
    if not lead_score:
        raise HTTPException(status_code=404, detail="Lead score not found")
    
    scoring_engine = LeadScoringEngine(db)
    explanation = scoring_engine.get_score_explanation(lead_score)
    
    return LeadScoreExplanation(**explanation)


@router.get("/leads/scores", response_model=List[LeadScoreResponse])
async def get_all_lead_scores(
    category: Optional[str] = Query(None, description="Filter by category: hot, warm, cold"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all lead scores for the current user with filtering options
    """
    # Build query
    query = db.query(LeadScore).join(FormSubmission).filter(
        FormSubmission.user_id == current_user.id
    )
    
    # Apply filters
    if category:
        query = query.filter(LeadScore.score_category == category)
    
    if min_score is not None:
        query = query.filter(LeadScore.final_score >= min_score)
    
    if max_score is not None:
        query = query.filter(LeadScore.final_score <= max_score)
    
    if date_from:
        query = query.filter(LeadScore.calculated_at >= date_from)
    
    if date_to:
        query = query.filter(LeadScore.calculated_at <= date_to)
    
    # Order by score (highest first) and apply pagination
    lead_scores = query.order_by(LeadScore.final_score.desc()).offset(offset).limit(limit).all()
    
    return lead_scores


@router.post("/leads/scores/batch", response_model=List[LeadScoreResponse])
async def calculate_batch_scores(
    submission_ids: List[UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate lead scores for multiple submissions at once
    """
    # Verify all submissions belong to user
    submissions = db.query(FormSubmission).filter(
        FormSubmission.id.in_(submission_ids),
        FormSubmission.user_id == current_user.id
    ).all()
    
    if len(submissions) != len(submission_ids):
        raise HTTPException(status_code=404, detail="Some submissions not found or unauthorized")
    
    scoring_engine = LeadScoringEngine(db)
    lead_scores = []
    
    for submission in submissions:
        # Check if score already exists
        existing_score = db.query(LeadScore).filter(
            LeadScore.submission_id == submission.id
        ).first()
        
        if not existing_score:
            lead_score = await scoring_engine.calculate_lead_score(
                submission.id,
                submission.form_data
            )
            lead_scores.append(lead_score)
        else:
            lead_scores.append(existing_score)
    
    return lead_scores


@router.get("/leads/stats")
async def get_lead_statistics(
    date_from: Optional[datetime] = Query(None, description="Start date for statistics"),
    date_to: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistical overview of lead scores
    """
    # Build base query
    query = db.query(LeadScore).join(FormSubmission).filter(
        FormSubmission.user_id == current_user.id
    )
    
    # Apply date filters
    if date_from:
        query = query.filter(LeadScore.calculated_at >= date_from)
    if date_to:
        query = query.filter(LeadScore.calculated_at <= date_to)
    
    all_scores = query.all()
    
    if not all_scores:
        return {
            "total_leads": 0,
            "average_score": 0,
            "category_breakdown": {},
            "score_distribution": {}
        }
    
    # Calculate statistics
    total_leads = len(all_scores)
    scores = [s.final_score for s in all_scores]
    average_score = sum(scores) / total_leads
    
    # Category breakdown
    category_counts = {"hot": 0, "warm": 0, "cold": 0}
    for score in all_scores:
        category_counts[score.score_category] += 1
    
    # Score distribution (by deciles)
    distribution = {f"{i*10}-{(i+1)*10}": 0 for i in range(10)}
    for score in scores:
        decile = min(9, score // 10)
        key = f"{decile*10}-{(decile+1)*10}"
        distribution[key] += 1
    
    return {
        "total_leads": total_leads,
        "average_score": round(average_score, 1),
        "category_breakdown": category_counts,
        "category_percentages": {
            k: round(v/total_leads * 100, 1) 
            for k, v in category_counts.items()
        },
        "score_distribution": distribution,
        "highest_score": max(scores),
        "lowest_score": min(scores),
        "hot_leads_count": category_counts["hot"],
        "conversion_ready": sum(1 for s in scores if s >= 70)
    }