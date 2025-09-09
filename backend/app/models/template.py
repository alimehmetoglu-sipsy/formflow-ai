from sqlalchemy import Column, String, JSON, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class DashboardTemplate(Base):
    __tablename__ = "dashboard_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, index=True)  # survey_analysis, customer_feedback, etc.
    icon = Column(String)
    thumbnail_url = Column(String)
    widgets = Column(JSON)  # Widget configurations
    theme = Column(JSON)  # Theme configuration
    layout = Column(JSON)  # Layout configuration
    is_system = Column(Boolean, default=False)  # System templates vs user templates
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    rating = Column(Integer)
    tags = Column(JSON)  # Array of tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    custom_templates = relationship("CustomTemplate", back_populates="template")

class CustomTemplate(Base):
    __tablename__ = "custom_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    template_id = Column(String, ForeignKey("dashboard_templates.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    widgets = Column(JSON)  # Custom widget configurations
    theme = Column(JSON)  # Custom theme
    layout = Column(JSON)  # Custom layout
    is_public = Column(Boolean, default=False)
    share_url = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="custom_templates")
    template = relationship("DashboardTemplate", back_populates="custom_templates")

class WidgetConfiguration(Base):
    __tablename__ = "widget_configurations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String, ForeignKey("dashboards.id"))
    widget_type = Column(String)  # chart, stats-card, table, etc.
    position = Column(JSON)  # {x, y, w, h}
    size = Column(String)  # small, medium, large, full-width
    title = Column(String)
    description = Column(Text)
    data_source = Column(JSON)  # Configuration for data source
    config = Column(JSON)  # Widget-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    dashboard = relationship("Dashboard", back_populates="widget_configurations")