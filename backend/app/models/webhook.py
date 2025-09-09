from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
import secrets

def generate_webhook_token():
    """Generate a secure webhook token"""
    return f"wh_{secrets.token_urlsafe(32)}"

class WebhookConfig(Base):
    __tablename__ = "webhook_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    webhook_token = Column(String, unique=True, nullable=False, default=generate_webhook_token)
    platform = Column(String, default="custom")  # jotform, microsoft_forms, surveymonkey, custom, etc.
    field_mappings = Column(JSON, default={})
    signature_secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="webhook_configs")
    webhook_logs = relationship("WebhookLog", back_populates="webhook_config", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "webhook_token": self.webhook_token,
            "platform": self.platform,
            "field_mappings": self.field_mappings,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_config_id = Column(String, ForeignKey("webhook_configs.id"), nullable=False)
    status = Column(String, nullable=False)  # success, error, processing
    request_body = Column(JSON)
    response_body = Column(JSON)
    error_message = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    webhook_config = relationship("WebhookConfig", back_populates="webhook_logs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "request_body": self.request_body,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }