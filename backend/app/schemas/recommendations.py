"""
Pydantic Schemas for Follow-up Recommendations (FA-47)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class RecommendationPriority(str, Enum):
    """Priority levels for recommendations"""
    high = "high"
    medium = "medium"
    low = "low"


class RecommendationMethod(str, Enum):
    """Follow-up methods"""
    call = "call"
    email = "email"
    demo = "demo"
    meeting = "meeting"
    linkedin = "linkedin"
    nurture = "nurture"


class RecommendationBase(BaseModel):
    """Base schema for recommendations"""
    action: str = Field(..., description="Recommended action to take")
    priority: RecommendationPriority
    timing: str = Field(..., description="When to take the action")
    method: RecommendationMethod
    reason: Optional[str] = Field(None, description="Why this action is recommended")


class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations"""
    lead_id: UUID
    include_templates: bool = True
    include_scripts: bool = True


class BulkRecommendationsRequest(BaseModel):
    """Request schema for bulk recommendation generation"""
    lead_ids: List[UUID]
    include_templates: bool = False


class RecommendationResponse(RecommendationBase):
    """Response schema for recommendations"""
    id: str
    lead_id: UUID
    template: Optional[str] = Field(None, description="Email template or call script")
    success_probability: Optional[float] = Field(None, ge=0, le=100)
    generated_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationFeedback(BaseModel):
    """Schema for recommendation feedback"""
    outcome: str = Field(..., description="Outcome: converted, in_progress, lost, not_followed")
    notes: Optional[str] = Field(None, description="Additional notes about the outcome")
    actual_action_taken: Optional[str] = None
    time_to_action: Optional[int] = Field(None, description="Hours until action was taken")


class RecommendationTemplate(BaseModel):
    """Schema for recommendation templates"""
    type: RecommendationMethod
    category: str = Field(..., description="hot, warm, or cold")
    subject: Optional[str] = Field(None, description="Email subject line")
    body: str = Field(..., description="Template body content")
    variables: List[str] = Field(..., description="Variables that need to be replaced")


class RecommendationEffectiveness(BaseModel):
    """Schema for recommendation effectiveness metrics"""
    total_recommendations: int
    followed_recommendations: int
    follow_rate: float
    outcomes: Dict[str, int]
    best_performing: Dict[str, Any]
    method_effectiveness: Dict[str, float]