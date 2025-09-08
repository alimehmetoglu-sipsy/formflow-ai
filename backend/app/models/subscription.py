from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    UNPAID = "unpaid"

class PlanType(enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"

class InvoiceStatus(enum.Enum):
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    lemonsqueezy_subscription_id = Column(String, unique=True, nullable=False)
    lemonsqueezy_order_id = Column(String, nullable=True)
    lemonsqueezy_product_id = Column(String, nullable=True)
    lemonsqueezy_variant_id = Column(String, nullable=True)
    
    # Plan information
    plan_type = Column(Enum(PlanType), nullable=False)
    plan_name = Column(String, nullable=False)
    
    # Subscription status and dates
    status = Column(Enum(SubscriptionStatus), nullable=False)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Pricing information
    unit_price = Column(Integer, nullable=False)  # in cents
    currency = Column(String, default="USD")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usage_records = relationship("Usage", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")

class Usage(Base):
    __tablename__ = "usage"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True)
    
    # Time period (YYYY-MM format)
    month = Column(String, nullable=False, index=True)
    
    # Usage metrics
    form_count = Column(Integer, default=0)
    submission_count = Column(Integer, default=0)
    dashboard_views = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    storage_used = Column(Integer, default=0)  # in MB
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True)
    lemonsqueezy_invoice_id = Column(String, unique=True, nullable=False)
    lemonsqueezy_order_id = Column(String, nullable=True)
    
    # Invoice details
    invoice_number = Column(String, nullable=True)
    amount_total = Column(Integer, nullable=False)  # in cents
    amount_subtotal = Column(Integer, nullable=False)  # in cents
    amount_tax = Column(Integer, default=0)  # in cents
    amount_discount = Column(Integer, default=0)  # in cents
    currency = Column(String, default="USD")
    
    # Status and dates
    status = Column(Enum(InvoiceStatus), nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # URLs
    invoice_url = Column(Text, nullable=True)
    pdf_url = Column(Text, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    invoice_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Payment method details
    type = Column(String, nullable=False)  # card, paypal, etc.
    brand = Column(String, nullable=True)  # visa, mastercard, etc.
    last_four = Column(String, nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlanLimits(Base):
    __tablename__ = "plan_limits"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    plan_type = Column(Enum(PlanType), unique=True, nullable=False)
    
    # Limits
    max_forms = Column(Integer, nullable=False)
    max_submissions_per_month = Column(Integer, nullable=False)
    max_dashboard_views_per_month = Column(Integer, nullable=False)
    max_api_calls_per_month = Column(Integer, nullable=False)
    max_storage_mb = Column(Integer, nullable=False)
    
    # Features
    custom_branding = Column(Boolean, default=False)
    api_access = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    white_label = Column(Boolean, default=False)
    custom_integrations = Column(Boolean, default=False)
    sla_guarantee = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)