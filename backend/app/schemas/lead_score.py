"""
Pydantic Schemas for Lead Scoring (FA-45)
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime


class LeadScoreBase(BaseModel):
    """Base schema for lead scores"""
    final_score: int = Field(..., ge=0, le=100, description="Final lead score (0-100)")
    score_category: str = Field(..., description="Category: hot, warm, or cold")
    

class LeadScoreCreate(BaseModel):
    """Schema for creating a lead score"""
    submission_id: UUID
    force_recalculate: bool = False


class ScoreFactorDetail(BaseModel):
    """Details about a scoring factor"""
    value: int = Field(..., description="Points for this factor")
    weight: float = Field(..., description="Weight of this factor")
    contribution: Optional[float] = Field(None, description="Weighted contribution to total")


class LeadScoreResponse(LeadScoreBase):
    """Response schema for lead scores"""
    id: UUID
    submission_id: UUID
    base_score: int
    ai_adjustment: int
    score_factors: Dict[str, ScoreFactorDetail]
    ai_insights: Optional[Dict[str, Any]] = None
    buying_signals_detected: Optional[List[str]] = None
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class LeadScoreExplanation(BaseModel):
    """Detailed explanation of lead score calculation"""
    total_score: int
    category: str
    breakdown: List[Dict[str, Any]]
    ai_bonus: Optional[Dict[str, Any]] = None


class ScoringRuleBase(BaseModel):
    """Base schema for scoring rules"""
    name: str
    field_name: str
    rule_type: str
    conditions: Dict[str, Any]
    weight: float = 1.0
    max_points: int


class ScoringRuleCreate(ScoringRuleBase):
    """Schema for creating a scoring rule"""
    is_active: bool = True


class ScoringRuleUpdate(BaseModel):
    """Schema for updating a scoring rule"""
    name: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    weight: Optional[float] = None
    max_points: Optional[int] = None
    is_active: Optional[bool] = None


class ScoringRuleResponse(ScoringRuleBase):
    """Response schema for scoring rules"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeadScoreStats(BaseModel):
    """Statistics about lead scores"""
    total_leads: int
    average_score: float
    category_breakdown: Dict[str, int]
    category_percentages: Dict[str, float]
    score_distribution: Dict[str, int]
    highest_score: int
    lowest_score: int
    hot_leads_count: int
    conversion_ready: int