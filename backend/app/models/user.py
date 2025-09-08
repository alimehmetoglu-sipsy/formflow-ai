from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from app.database import Base
from passlib.context import CryptContext
import uuid
from datetime import datetime
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PlanType(enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Null for OAuth users
    full_name = Column(String)
    avatar_url = Column(String)
    
    # OAuth fields
    google_id = Column(String, unique=True, nullable=True)
    oauth_provider = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Subscription
    plan_type = Column(SQLEnum(PlanType), default=PlanType.FREE)
    subscription_tier = Column(String, default="free")  # free, pro, business
    subscription_status = Column(String, default="inactive")  # active, cancelled, expired
    subscription_id = Column(String, nullable=True)  # LemonSqueezy subscription ID
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    typeform_connected = Column(Boolean, default=False)
    typeform_api_key = Column(String, nullable=True)
    
    @property
    def name(self):
        """Return name (alias for full_name for compatibility)"""
        return self.full_name
    
    @name.setter
    def name(self, value):
        """Set name (alias for full_name for compatibility)"""
        self.full_name = value
    
    def verify_password(self, plain_password: str) -> bool:
        if not self.hashed_password:
            return False
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)