"""
Team Collaboration Models for FA-50
Database models for sales team collaboration and lead distribution
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class TeamRole(enum.Enum):
    """Team member roles"""
    MANAGER = "manager"
    SENIOR_REP = "senior_rep"
    REP = "rep"
    JUNIOR_REP = "junior_rep"
    VIEWER = "viewer"


class AssignmentMethod(enum.Enum):
    """Lead assignment methods"""
    ROUND_ROBIN = "round_robin"
    TERRITORY = "territory"
    SCORE_BASED = "score_based"
    CAPACITY = "capacity"
    EXPERTISE = "expertise"
    MANUAL = "manual"


class LeadStatus(enum.Enum):
    """Lead status in sales process"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CONVERTED = "converted"
    LOST = "lost"


class Team(Base):
    """Model for sales teams"""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Team settings
    settings = Column(JSON, default={})
    # Example: {
    #   "auto_assignment": true,
    #   "assignment_method": "round_robin",
    #   "sla_hours": 24,
    #   "notification_preferences": {...}
    # }
    
    # Assignment rules
    assignment_rules = Column(JSON, default=[])
    # Example: [
    #   {"type": "score", "condition": ">=80", "assign_to": "senior_reps"},
    #   {"type": "territory", "condition": "west_coast", "assign_to": "user_123"}
    # ]
    
    # Team goals
    monthly_target = Column(Float, default=0)
    quarterly_target = Column(Float, default=0)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("User", foreign_keys=[manager_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    lead_assignments = relationship("LeadAssignment", back_populates="team")


class TeamMember(Base):
    """Model for team members"""
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Role and permissions
    role = Column(SQLEnum(TeamRole), default=TeamRole.REP)
    
    # Territories and specialization
    territories = Column(JSON, default=[])  # ["west_coast", "midwest"]
    industries = Column(JSON, default=[])  # ["saas", "healthcare"]
    expertise = Column(JSON, default=[])  # ["enterprise", "smb"]
    languages = Column(JSON, default=[])  # ["english", "spanish"]
    
    # Capacity and workload
    max_capacity = Column(Integer, default=50)  # Max leads at once
    current_capacity = Column(Integer, default=0)
    daily_lead_limit = Column(Integer, default=10)
    leads_assigned_today = Column(Integer, default=0)
    
    # Performance metrics
    total_leads_assigned = Column(Integer, default=0)
    total_conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)  # hours
    average_deal_size = Column(Float, default=0.0)
    
    # Availability
    is_available = Column(Boolean, default=True)
    out_of_office_until = Column(DateTime, nullable=True)
    
    # Assignment preferences
    preferred_lead_score_min = Column(Integer, default=0)
    preferred_lead_score_max = Column(Integer, default=100)
    preferred_deal_size_min = Column(Float, default=0)
    
    # Metadata
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_assignment_at = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")
    assignments = relationship("LeadAssignment", back_populates="assigned_to_member")


class LeadAssignment(Base):
    """Model for lead assignments to team members"""
    __tablename__ = "lead_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Assignment details
    assignment_method = Column(SQLEnum(AssignmentMethod), default=AssignmentMethod.MANUAL)
    assignment_reason = Column(String(500))
    priority = Column(Integer, default=0)  # 0=low, 1=medium, 2=high, 3=urgent
    
    # Lead information snapshot
    lead_score = Column(Integer)
    lead_data_snapshot = Column(JSON)  # Form data at time of assignment
    
    # Status tracking
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
    
    # Timeline
    assigned_at = Column(DateTime, default=datetime.utcnow)
    first_contact_at = Column(DateTime, nullable=True)
    last_contact_at = Column(DateTime, nullable=True)
    qualified_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)
    lost_at = Column(DateTime, nullable=True)
    
    # Activity tracking
    contact_attempts = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    calls_made = Column(Integer, default=0)
    meetings_scheduled = Column(Integer, default=0)
    
    # Outcome
    deal_size = Column(Float, nullable=True)
    lost_reason = Column(String(500), nullable=True)
    competitor_won = Column(String(255), nullable=True)
    
    # Notes and collaboration
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)  # Not visible to customer
    
    # SLA tracking
    sla_deadline = Column(DateTime, nullable=True)
    sla_met = Column(Boolean, nullable=True)
    
    # Relationships
    lead = relationship("FormSubmission")
    team = relationship("Team", back_populates="lead_assignments")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    assigned_to_member = relationship("TeamMember", 
                                    foreign_keys=[assigned_to],
                                    primaryjoin="LeadAssignment.assigned_to==TeamMember.user_id")
    activities = relationship("LeadActivity", back_populates="assignment")


class LeadActivity(Base):
    """Model for tracking lead activities"""
    __tablename__ = "lead_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("lead_assignments.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Activity details
    activity_type = Column(String(50))  # call, email, meeting, note, status_change
    activity_data = Column(JSON)
    # Example: {
    #   "duration": 15,  # for calls
    #   "subject": "Follow-up email",  # for emails
    #   "old_status": "new", "new_status": "contacted"  # for status changes
    # }
    
    description = Column(Text, nullable=True)
    outcome = Column(String(255), nullable=True)
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assignment = relationship("LeadAssignment", back_populates="activities")
    user = relationship("User")


class AssignmentRule(Base):
    """Model for automated assignment rules"""
    __tablename__ = "assignment_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    rule_type = Column(String(50))  # score_based, territory, round_robin, etc.
    conditions = Column(JSON)
    # Example for score-based:
    # {"score_min": 80, "score_max": 100}
    # Example for territory:
    # {"field": "state", "values": ["CA", "OR", "WA"]}
    
    # Assignment target
    assign_to_type = Column(String(50))  # specific_user, role, team, round_robin
    assign_to_target = Column(JSON)
    # Example: {"user_id": "123"} or {"role": "senior_rep"}
    
    # Priority and order
    priority = Column(Integer, default=0)  # Higher priority rules evaluated first
    is_active = Column(Boolean, default=True)
    
    # Statistics
    times_triggered = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamPerformanceSnapshot(Base):
    """Model for tracking team performance over time"""
    __tablename__ = "team_performance_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    
    # Team metrics
    total_leads = Column(Integer, default=0)
    total_contacted = Column(Integer, default=0)
    total_qualified = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    
    # Performance metrics
    average_response_time = Column(Float)  # hours
    average_conversion_time = Column(Float)  # days
    conversion_rate = Column(Float)
    total_revenue = Column(Float)
    
    # Member breakdown
    member_stats = Column(JSON)
    # Example: {
    #   "user_123": {"leads": 10, "conversions": 3, "revenue": 50000},
    #   "user_456": {"leads": 8, "conversions": 2, "revenue": 30000}
    # }
    
    # SLA metrics
    sla_met_percentage = Column(Float)
    average_time_to_first_contact = Column(Float)  # hours
    
    created_at = Column(DateTime, default=datetime.utcnow)