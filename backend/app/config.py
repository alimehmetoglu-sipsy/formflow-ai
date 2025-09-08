from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FormFlow AI"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://formflow:formflow123@localhost:5432/formflow_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Typeform
    TYPEFORM_WEBHOOK_SECRET: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Payment
    LEMONSQUEEZY_API_KEY: Optional[str] = None
    LEMONSQUEEZY_STORE_ID: Optional[str] = None
    LEMONSQUEEZY_WEBHOOK_SECRET: Optional[str] = None
    LEMONSQUEEZY_PRO_VARIANT_ID: Optional[str] = None
    LEMONSQUEEZY_BUSINESS_VARIANT_ID: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    POSTHOG_API_KEY: Optional[str] = None
    
    # Email
    RESEND_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()