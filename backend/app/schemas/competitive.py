"""
Pydantic Schemas for Competitive Analysis (FA-49)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class CompetitorCategory(str, Enum):
    """Competitor categories"""
    enterprise_crm = "enterprise_crm"
    marketing_automation = "marketing_automation"
    sales_crm = "sales_crm"
    manual_process = "manual_process"
    custom_solution = "custom_solution"
    no_solution = "no_solution"


class CompetitiveOutcome(str, Enum):
    """Competitive deal outcomes"""
    won = "won"
    lost = "lost"
    no_decision = "no_decision"
    in_progress = "in_progress"


class CompetitorProfileBase(BaseModel):
    """Base schema for competitor profiles"""
    name: str
    display_name: str
    target_market: Optional[str] = None
    is_active: bool = True


class CompetitorProfileResponse(CompetitorProfileBase):
    """Response schema for competitor profiles"""
    id: UUID
    strengths: List[str]
    weaknesses: List[str]
    our_advantages: List[str]
    their_advantages: List[str]
    positioning_strategy: Optional[str]
    key_differentiators: List[str]
    win_rate: float
    total_competitions: int
    wins_against: int
    losses_against: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompetitiveInsightBase(BaseModel):
    """Base schema for competitive insights"""
    submission_id: UUID
    competitors_detected: List[str]
    current_solution: Optional[str]


class CompetitiveInsightResponse(CompetitiveInsightBase):
    """Response schema for competitive insights"""
    id: UUID
    competitor_id: Optional[UUID]
    detection_method: str
    confidence_score: float
    mention_context: Optional[str]
    positioning_strategy: Optional[str]
    recommended_approach: Optional[List[str]]
    battle_points: Optional[List[str]]
    risk_factors: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class BattleCardResponse(BaseModel):
    """Response schema for battle cards"""
    competitor_name: str
    battle_card: Dict[str, Any]
    last_updated: datetime
    
    class Config:
        from_attributes = True


class ObjectionHandlerBase(BaseModel):
    """Base schema for objection handlers"""
    objection_type: str
    objection_text: str
    response_framework: str
    response_script: str


class ObjectionHandlerResponse(ObjectionHandlerBase):
    """Response schema for objection handlers"""
    id: UUID
    competitor_id: UUID
    supporting_evidence: Optional[List[Dict]]
    usage_count: int
    success_rate: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CompetitiveOutcomeRequest(BaseModel):
    """Request schema for tracking competitive outcomes"""
    lead_id: UUID
    competitor_name: str
    outcome: CompetitiveOutcome
    deal_size: Optional[float] = None
    primary_reason: Optional[str] = None
    what_worked: Optional[str] = None
    what_didnt_work: Optional[str] = None
    recommendations: Optional[str] = None
    sales_cycle_days: Optional[int] = None


class CompetitorComparisonResponse(BaseModel):
    """Response schema for competitor comparisons"""
    competitors: List[Dict[str, Any]]
    feature_matrix: List[Dict[str, Any]]
    pricing_comparison: Optional[List[Dict]]
    our_advantages: Dict[str, List[str]]
    
    class Config:
        from_attributes = True


class BattleCardSection(BaseModel):
    """Schema for battle card sections"""
    executive_summary: Optional[str]
    elevator_pitch: Optional[str]
    value_proposition: Optional[str]
    feature_comparison: List[Dict[str, str]]
    pricing_comparison: Optional[Dict]
    proof_points: List[str]
    discovery_questions: List[str]
    demo_focus_areas: List[str]
    trap_setting_questions: List[str]
    switching_playbook: Optional[Dict]
    competitive_landmines: List[str]
    customer_wins: Optional[List[Dict]]


class CompetitiveStatsResponse(BaseModel):
    """Response schema for competitive statistics"""
    overall: Dict[str, Any]
    by_competitor: Dict[str, Dict]
    recent_trends: Optional[Dict]
    top_competitors: Optional[List[str]]
    win_rate_trend: Optional[List[Dict]]