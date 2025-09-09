"""
Competitive Analysis Models for FA-49
Database models for competitive intelligence and battle cards
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class CompetitorProfile(Base):
    """Model for storing competitor information"""
    __tablename__ = "competitor_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255))
    
    # Company information
    company_info = Column(JSON)  # website, founded, size, revenue, etc.
    
    # Product details
    product_features = Column(JSON)
    pricing_tiers = Column(JSON)
    target_market = Column(String(500))
    
    # Strengths and weaknesses
    strengths = Column(JSON)  # List of strengths
    weaknesses = Column(JSON)  # List of weaknesses
    
    # Our advantages
    our_advantages = Column(JSON)  # List of advantages we have
    their_advantages = Column(JSON)  # List of advantages they have
    
    # Positioning
    positioning_strategy = Column(Text)
    key_differentiators = Column(JSON)
    
    # Win/Loss data
    total_competitions = Column(Integer, default=0)
    wins_against = Column(Integer, default=0)
    losses_against = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # Battle card
    battle_card = Column(JSON)  # Complete battle card data
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competitive_insights = relationship("CompetitiveInsight", back_populates="competitor")
    objection_handlers = relationship("ObjectionHandler", back_populates="competitor")


class CompetitiveInsight(Base):
    """Model for storing competitive insights from form submissions"""
    __tablename__ = "competitive_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"), nullable=False)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_profiles.id"))
    
    # Detection details
    competitors_detected = Column(JSON)  # List of competitor names detected
    detection_method = Column(String(50))  # 'explicit', 'implicit', 'ai_detected'
    confidence_score = Column(Float)  # 0-1 confidence in detection
    
    # Context from form
    mention_context = Column(Text)  # Text where competitor was mentioned
    current_solution = Column(String(500))
    evaluation_criteria = Column(JSON)
    decision_timeline = Column(String(255))
    
    # Generated insights
    positioning_strategy = Column(Text)
    recommended_approach = Column(JSON)
    battle_points = Column(JSON)  # Key points to emphasize
    risk_factors = Column(JSON)  # Risks to address
    
    # Outcome tracking
    outcome = Column(String(50))  # 'won', 'lost', 'in_progress', 'no_decision'
    outcome_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="competitive_insight")
    competitor = relationship("CompetitorProfile", back_populates="competitive_insights")


class ObjectionHandler(Base):
    """Model for storing objection handling scripts"""
    __tablename__ = "objection_handlers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_profiles.id"))
    
    objection_type = Column(String(100))  # 'price', 'features', 'integration', 'support', etc.
    objection_text = Column(Text)  # Common objection phrasing
    
    # Response strategy
    response_framework = Column(String(50))  # 'acknowledge_redirect', 'reframe', 'evidence'
    response_script = Column(Text)
    supporting_evidence = Column(JSON)  # Case studies, stats, testimonials
    
    # Effectiveness
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competitor = relationship("CompetitorProfile", back_populates="objection_handlers")


class BattleCard(Base):
    """Model for storing battle card templates and versions"""
    __tablename__ = "battle_cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_profiles.id"))
    version = Column(String(20))
    
    # Battle card sections
    executive_summary = Column(Text)
    
    # Comparison grid
    feature_comparison = Column(JSON)
    # Example: [
    #   {"feature": "AI Analysis", "us": "✓ Advanced", "them": "✗ Basic"},
    #   {"feature": "Setup Time", "us": "5 minutes", "them": "2+ weeks"}
    # ]
    
    pricing_comparison = Column(JSON)
    
    # Positioning
    elevator_pitch = Column(Text)
    value_proposition = Column(Text)
    proof_points = Column(JSON)  # List of evidence/testimonials
    
    # Sales enablement
    discovery_questions = Column(JSON)  # Questions to uncover pain points
    demo_focus_areas = Column(JSON)  # What to emphasize in demo
    trap_setting_questions = Column(JSON)  # Questions that highlight our strengths
    
    # Common scenarios
    switching_playbook = Column(JSON)  # How to help them switch
    competitive_landmines = Column(JSON)  # Topics to avoid
    
    # Resources
    customer_wins = Column(JSON)  # Case studies of wins against this competitor
    sales_tools = Column(JSON)  # Links to comparison sheets, ROI calculators
    
    # Metadata
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class CompetitiveOutcome(Base):
    """Model for tracking win/loss against competitors"""
    __tablename__ = "competitive_outcomes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"))
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitor_profiles.id"))
    
    # Outcome details
    outcome = Column(String(20), nullable=False)  # 'won', 'lost', 'no_decision'
    outcome_date = Column(DateTime)
    
    # Deal details
    deal_size = Column(Float)
    contract_length = Column(Integer)  # months
    product_tier = Column(String(50))
    
    # Win/Loss analysis
    primary_reason = Column(String(500))
    contributing_factors = Column(JSON)
    competitor_strengths_shown = Column(JSON)
    our_strengths_shown = Column(JSON)
    
    # Lessons learned
    what_worked = Column(Text)
    what_didnt_work = Column(Text)
    recommendations = Column(Text)
    
    # Sales process details
    sales_rep_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sales_cycle_days = Column(Integer)
    touchpoints = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # For analysis
    tags = Column(JSON)  # Industry, company size, use case, etc.