"""
Lead Scoring Model for FA-45
Database model for storing lead scores and scoring metadata
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class LeadScore(Base):
    """Model for storing lead scores and scoring breakdown"""
    __tablename__ = "lead_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"), nullable=False)
    
    # Score components
    base_score = Column(Integer, nullable=False)
    ai_adjustment = Column(Integer, default=0)
    final_score = Column(Integer, nullable=False)
    
    # Score factors breakdown
    score_factors = Column(JSON, nullable=False)
    # Example: {
    #   "budget": {"value": 30, "reason": "Budget >$50k"},
    #   "timeline": {"value": 25, "reason": "Timeline <3 months"},
    #   "authority": {"value": 20, "reason": "Decision maker"},
    #   "need": {"value": 15, "reason": "Clear pain points"},
    #   "company_size": {"value": 10, "reason": "Enterprise"}
    # }
    
    # Score category
    score_category = Column(String(50))  # 'hot', 'warm', 'cold'
    
    # AI insights
    ai_insights = Column(JSON)
    buying_signals_detected = Column(JSON)
    
    # Metadata
    scoring_version = Column(String(50), default="v1.0")
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="lead_score")


class ScoringRule(Base):
    """Model for configurable scoring rules"""
    __tablename__ = "scoring_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    field_name = Column(String(255), nullable=False)
    
    # Rule configuration
    rule_type = Column(String(50))  # 'numeric', 'text', 'select', 'boolean'
    conditions = Column(JSON)
    # Example for numeric: {"operator": ">=", "value": 50000}
    # Example for text: {"contains": ["urgent", "asap", "immediately"]}
    
    # Scoring
    weight = Column(Float, default=1.0)
    max_points = Column(Integer, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeadScoreHistory(Base):
    """Model for tracking lead score changes over time"""
    __tablename__ = "lead_score_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_score_id = Column(UUID(as_uuid=True), ForeignKey("lead_scores.id"), nullable=False)
    
    previous_score = Column(Integer)
    new_score = Column(Integer)
    change_reason = Column(String(500))
    
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))