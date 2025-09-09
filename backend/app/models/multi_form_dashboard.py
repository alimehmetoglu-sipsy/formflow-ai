"""
Multi-Form Dashboard Models for FA-44 Epic
Enables aggregation of data from multiple forms into a single dashboard
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class MultiFormDashboard(Base):
    """
    Represents a dashboard that aggregates data from multiple form sources
    """
    __tablename__ = "multi_form_dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Configuration for aggregation
    aggregation_config = Column(JSON, nullable=False)
    # Example structure:
    # {
    #     "form_sources": [
    #         {"form_id": "uuid", "type": "typeform", "weight": 1.0},
    #         {"form_id": "uuid", "type": "google_forms", "weight": 1.0}
    #     ],
    #     "aggregation_method": "union|intersection|weighted",
    #     "conflict_resolution": "latest|average|priority"
    # }
    
    # Analytics configuration
    analytics_config = Column(JSON)
    # Example structure:
    # {
    #     "metrics": [
    #         {"name": "total_responses", "formula": "sum(responses)"},
    #         {"name": "avg_satisfaction", "formula": "avg(satisfaction_score)"}
    #     ],
    #     "kpis": [
    #         {"name": "conversion_rate", "target": 0.25, "formula": "converted/total"}
    #     ]
    # }
    
    # Filter configuration
    filter_config = Column(JSON)
    # Example structure:
    # {
    #     "date_range": {"start": "2025-01-01", "end": "2025-12-31"},
    #     "segments": ["age_group", "location"],
    #     "custom_filters": [{"field": "score", "operator": ">", "value": 7}]
    # }
    
    # Cached aggregated data
    cached_data = Column(JSON)
    cache_updated_at = Column(DateTime)
    
    # Dashboard settings
    is_public = Column(Boolean, default=False)
    share_token = Column(String(255), unique=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("dashboard_templates.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="multi_form_dashboards")
    form_mappings = relationship("MultiFormMapping", back_populates="dashboard", cascade="all, delete-orphan")
    scheduled_reports = relationship("ScheduledReport", back_populates="dashboard", cascade="all, delete-orphan")
    custom_metrics = relationship("CustomMetric", back_populates="dashboard", cascade="all, delete-orphan")


class MultiFormMapping(Base):
    """
    Maps individual forms to a multi-form dashboard
    """
    __tablename__ = "multi_form_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("multi_form_dashboards.id"), nullable=False)
    form_submission_id = Column(UUID(as_uuid=True), ForeignKey("form_submissions.id"))
    
    # Form identification
    form_type = Column(String(50))  # 'typeform', 'google_forms', 'custom'
    form_external_id = Column(String(255))  # External form ID from platform
    form_title = Column(String(255))
    
    # Field mapping configuration
    field_mappings = Column(JSON)
    # Example structure:
    # {
    #     "name": "respondent_name",
    #     "email": "contact_email",
    #     "score": "satisfaction_score"
    # }
    
    # Aggregation settings
    weight = Column(Float, default=1.0)  # Weight for weighted aggregation
    priority = Column(Integer, default=0)  # Priority for conflict resolution
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_responses = Column(Integer, default=0)
    last_response_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("MultiFormDashboard", back_populates="form_mappings")


class CustomMetric(Base):
    """
    Custom metrics and KPIs defined for multi-form dashboards
    """
    __tablename__ = "custom_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("multi_form_dashboards.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    display_name = Column(String(255))
    description = Column(Text)
    
    # Metric definition
    metric_type = Column(String(50))  # 'calculated', 'aggregated', 'kpi'
    formula = Column(Text, nullable=False)  # Mathematical formula or aggregation rule
    unit = Column(String(50))  # 'percentage', 'number', 'currency', etc.
    
    # Visualization settings
    visualization_type = Column(String(50))  # 'gauge', 'line', 'bar', 'number'
    visualization_config = Column(JSON)
    
    # KPI settings (if applicable)
    is_kpi = Column(Boolean, default=False)
    target_value = Column(Float)
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    
    # Calculation cache
    last_calculated_value = Column(Float)
    last_calculated_at = Column(DateTime)
    
    # Alert settings
    enable_alerts = Column(Boolean, default=False)
    alert_config = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("MultiFormDashboard", back_populates="custom_metrics")


class ScheduledReport(Base):
    """
    Scheduled reports for multi-form dashboards
    """
    __tablename__ = "scheduled_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("multi_form_dashboards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Schedule configuration
    schedule_type = Column(String(50))  # 'daily', 'weekly', 'monthly', 'custom'
    schedule_config = Column(JSON)
    # Example structure:
    # {
    #     "time": "09:00",
    #     "timezone": "UTC",
    #     "days_of_week": [1, 3, 5],  # For weekly
    #     "day_of_month": 1,  # For monthly
    #     "cron_expression": "0 9 * * MON,WED,FRI"  # For custom
    # }
    
    # Report configuration
    report_format = Column(String(20))  # 'pdf', 'excel', 'csv', 'html'
    include_sections = Column(JSON)  # List of sections to include
    filter_override = Column(JSON)  # Override dashboard filters for this report
    
    # Recipients
    recipients = Column(JSON)  # List of email addresses
    # Example structure:
    # {
    #     "to": ["manager@company.com"],
    #     "cc": ["team@company.com"],
    #     "bcc": []
    # }
    
    # Email settings
    email_subject = Column(String(255))
    email_body_template = Column(Text)
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime)
    last_run_status = Column(String(50))  # 'success', 'failed', 'partial'
    last_run_error = Column(Text)
    next_run_at = Column(DateTime)
    
    # Statistics
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    failed_runs = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dashboard = relationship("MultiFormDashboard", back_populates="scheduled_reports")
    user = relationship("User")


class AggregationJob(Base):
    """
    Tracks aggregation job status for async processing
    """
    __tablename__ = "aggregation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("multi_form_dashboards.id"), nullable=False)
    
    job_type = Column(String(50))  # 'full_refresh', 'incremental', 'real_time'
    status = Column(String(50))  # 'pending', 'processing', 'completed', 'failed'
    
    # Progress tracking
    total_forms = Column(Integer)
    processed_forms = Column(Integer, default=0)
    total_records = Column(Integer)
    processed_records = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    estimated_completion = Column(DateTime)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Results
    result_summary = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)