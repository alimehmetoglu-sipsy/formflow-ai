"""
API Endpoints for Competitive Analysis (FA-49)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.form import FormSubmission
from app.models.competitive_analysis import (
    CompetitorProfile,
    CompetitiveInsight,
    ObjectionHandler,
    CompetitiveOutcome
)
from app.services.competitive_analysis import CompetitiveAnalysisService
from app.schemas.competitive import (
    CompetitorProfileResponse,
    CompetitiveInsightResponse,
    BattleCardResponse,
    ObjectionHandlerResponse,
    CompetitiveOutcomeRequest,
    CompetitorComparisonResponse
)

router = APIRouter()


@router.post("/leads/{lead_id}/competitive-analysis", response_model=CompetitiveInsightResponse)
async def analyze_competition(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a lead for competitive intelligence
    """
    # Verify lead ownership
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == lead_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Check if analysis already exists
    existing_insight = db.query(CompetitiveInsight).filter(
        CompetitiveInsight.submission_id == lead_id
    ).first()
    
    if existing_insight:
        return existing_insight
    
    # Generate new analysis
    service = CompetitiveAnalysisService(db)
    insight = await service.analyze_competition(lead_id, submission.form_data)
    
    return insight


@router.get("/competitors", response_model=List[CompetitorProfileResponse])
async def get_competitors(
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all competitor profiles
    """
    query = db.query(CompetitorProfile)
    
    if is_active is not None:
        query = query.filter(CompetitorProfile.is_active == is_active)
    
    competitors = query.order_by(CompetitorProfile.win_rate.desc()).all()
    
    return competitors


@router.get("/competitors/{competitor_name}/battle-card", response_model=BattleCardResponse)
async def get_battle_card(
    competitor_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get battle card for specific competitor
    """
    service = CompetitiveAnalysisService(db)
    battle_card = service.get_battle_card(competitor_name.lower())
    
    if not battle_card:
        raise HTTPException(status_code=404, detail="Battle card not found")
    
    return BattleCardResponse(
        competitor_name=competitor_name,
        battle_card=battle_card,
        last_updated=datetime.utcnow()
    )


@router.get("/competitors/{competitor_id}/objections", response_model=List[ObjectionHandlerResponse])
async def get_objection_handlers(
    competitor_id: UUID,
    objection_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get objection handling scripts for competitor
    """
    query = db.query(ObjectionHandler).filter(
        ObjectionHandler.competitor_id == competitor_id,
        ObjectionHandler.is_active == True
    )
    
    if objection_type:
        query = query.filter(ObjectionHandler.objection_type == objection_type)
    
    handlers = query.order_by(ObjectionHandler.success_rate.desc()).all()
    
    return handlers


@router.post("/competitive-outcomes")
async def track_competitive_outcome(
    outcome_data: CompetitiveOutcomeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track win/loss outcome against a competitor
    """
    # Verify lead ownership
    submission = db.query(FormSubmission).filter(
        FormSubmission.id == outcome_data.lead_id,
        FormSubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get competitor
    competitor = db.query(CompetitorProfile).filter(
        CompetitorProfile.name == outcome_data.competitor_name.lower()
    ).first()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Track outcome
    service = CompetitiveAnalysisService(db)
    service.track_competitive_outcome(
        lead_id=outcome_data.lead_id,
        competitor_id=competitor.id,
        outcome=outcome_data.outcome,
        details=outcome_data.dict()
    )
    
    return {"status": "success", "message": "Outcome tracked"}


@router.get("/competitive-stats")
async def get_competitive_statistics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get competitive win/loss statistics
    """
    # Get all competitors with stats
    competitors = db.query(CompetitorProfile).filter(
        CompetitorProfile.total_competitions > 0
    ).all()
    
    stats = {
        "overall": {
            "total_competitions": sum(c.total_competitions for c in competitors),
            "total_wins": sum(c.wins_against for c in competitors),
            "total_losses": sum(c.losses_against for c in competitors),
            "overall_win_rate": 0
        },
        "by_competitor": {}
    }
    
    # Calculate overall win rate
    if stats["overall"]["total_competitions"] > 0:
        stats["overall"]["overall_win_rate"] = (
            stats["overall"]["total_wins"] / stats["overall"]["total_competitions"]
        )
    
    # Stats by competitor
    for comp in competitors:
        stats["by_competitor"][comp.name] = {
            "competitions": comp.total_competitions,
            "wins": comp.wins_against,
            "losses": comp.losses_against,
            "win_rate": comp.win_rate,
            "top_advantages": comp.our_advantages[:3] if comp.our_advantages else []
        }
    
    # Get recent outcomes if date range specified
    if date_from or date_to:
        query = db.query(CompetitiveOutcome)
        if date_from:
            query = query.filter(CompetitiveOutcome.outcome_date >= date_from)
        if date_to:
            query = query.filter(CompetitiveOutcome.outcome_date <= date_to)
        
        recent_outcomes = query.all()
        
        stats["recent_trends"] = {
            "period_wins": sum(1 for o in recent_outcomes if o.outcome == 'won'),
            "period_losses": sum(1 for o in recent_outcomes if o.outcome == 'lost'),
            "average_deal_size": sum(o.deal_size or 0 for o in recent_outcomes) / len(recent_outcomes) if recent_outcomes else 0
        }
    
    return stats


@router.get("/competitors/compare", response_model=CompetitorComparisonResponse)
async def compare_competitors(
    competitors: List[str] = Query(..., description="Competitor names to compare"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get side-by-side comparison of multiple competitors
    """
    if len(competitors) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 competitors for comparison")
    
    comparison = {
        "competitors": [],
        "feature_matrix": [],
        "pricing_comparison": [],
        "our_advantages": {}
    }
    
    for comp_name in competitors:
        competitor = db.query(CompetitorProfile).filter(
            CompetitorProfile.name == comp_name.lower()
        ).first()
        
        if competitor:
            comparison["competitors"].append({
                "name": competitor.display_name,
                "win_rate": competitor.win_rate,
                "strengths": competitor.strengths[:3] if competitor.strengths else [],
                "weaknesses": competitor.weaknesses[:3] if competitor.weaknesses else []
            })
            
            comparison["our_advantages"][competitor.name] = competitor.our_advantages[:5] if competitor.our_advantages else []
    
    # Add feature comparison matrix
    comparison["feature_matrix"] = [
        {"feature": "Setup Time", "formflow": "5 minutes", "competitors": {"salesforce": "2+ weeks", "hubspot": "1 week", "excel": "N/A"}},
        {"feature": "AI Analysis", "formflow": "Advanced", "competitors": {"salesforce": "Basic", "hubspot": "Basic", "excel": "None"}},
        {"feature": "Pricing Model", "formflow": "Per Dashboard", "competitors": {"salesforce": "Per User", "hubspot": "Per Contact", "excel": "One-time"}},
        {"feature": "Learning Curve", "formflow": "None", "competitors": {"salesforce": "Steep", "hubspot": "Moderate", "excel": "Low"}}
    ]
    
    return CompetitorComparisonResponse(**comparison)


@router.post("/battle-cards/generate")
async def generate_custom_battle_card(
    competitor_name: str,
    lead_context: Optional[Dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a custom battle card based on specific lead context
    """
    service = CompetitiveAnalysisService(db)
    
    # Get base battle card
    base_card = service.get_battle_card(competitor_name.lower())
    
    if not base_card:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Customize based on lead context if provided
    if lead_context:
        # Add context-specific positioning
        if 'industry' in lead_context:
            base_card['industry_positioning'] = f"Specific advantages for {lead_context['industry']}"
        
        if 'company_size' in lead_context:
            base_card['size_positioning'] = f"Perfect fit for {lead_context['company_size']} companies"
        
        if 'pain_points' in lead_context:
            base_card['pain_point_mapping'] = {
                pain: f"How FormFlow solves: {pain}"
                for pain in lead_context['pain_points']
            }
    
    return {
        "competitor": competitor_name,
        "battle_card": base_card,
        "customized_for": lead_context,
        "generated_at": datetime.utcnow()
    }