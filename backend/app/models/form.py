from sqlalchemy import Column, String, JSON, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    typeform_id = Column(String, index=True)
    form_title = Column(String)
    response_id = Column(String, unique=True)
    submitted_at = Column(DateTime)
    answers = Column(JSON)  # Store complete answer data
    processed = Column(Boolean, default=False)
    dashboard_url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    dashboard = relationship("Dashboard", back_populates="submission", uselist=False)

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, ForeignKey("form_submissions.id"))
    template_type = Column(String)  # diet_plan, lead_score, event, generic
    ai_generated_content = Column(JSON)
    html_content = Column(Text)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    submission = relationship("FormSubmission", back_populates="dashboard")