import logging
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import settings

# Google Cloud imports
try:
    from google.cloud import logging as cloud_logging
    from google.cloud import error_reporting
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Sentry imports  
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# Structured logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

logger = logging.getLogger(__name__)

def setup_monitoring():
    """Initialize monitoring and error tracking services"""
    
    # Google Cloud Logging for production
    if os.getenv("ENVIRONMENT") == "production" and GOOGLE_CLOUD_AVAILABLE:
        try:
            client = cloud_logging.Client()
            client.setup_logging()
            logger.info("✅ Google Cloud Logging initialized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Google Cloud Logging: {e}")
    
    # Structured logging setup
    if STRUCTLOG_AVAILABLE:
        setup_structured_logging()
    
    # Sentry for error tracking
    if settings.SENTRY_DSN and SENTRY_AVAILABLE:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment="production" if not settings.DEBUG else "development",
            release=getattr(settings, 'VERSION', '1.0.0'),
            send_default_pii=False,
            attach_stacktrace=True,
            max_breadcrumbs=50,
        )
        logger.info("✅ Sentry monitoring initialized")
    else:
        logger.warning("⚠️ Sentry not available or DSN not configured - error tracking disabled")
    
    # Setup basic logging
    setup_logging()

def setup_logging():
    """Configure structured logging"""
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def track_event(event_name: str, properties: dict = None):
    """Track custom events (can be extended with PostHog/Mixpanel later)"""
    logger.info(f"Event: {event_name}", extra={"properties": properties or {}})

def setup_structured_logging():
    """Configure structured logging with structlog"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

class FormFlowMonitor:
    """FormFlow AI monitoring utilities"""
    
    def __init__(self):
        self.error_client = None
        if os.getenv("ENVIRONMENT") == "production" and GOOGLE_CLOUD_AVAILABLE:
            try:
                self.error_client = error_reporting.Client()
            except Exception:
                pass
        
        # Use structlog if available, otherwise standard logger
        if STRUCTLOG_AVAILABLE:
            self.logger = structlog.get_logger(__name__)
        else:
            self.logger = logger
    
    def log_webhook_received(self, source: str, response_id: str, user_id: Optional[str] = None):
        """Log webhook reception"""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(
                "webhook_received",
                source=source,
                response_id=response_id,
                user_id=user_id,
                action="webhook_received"
            )
        else:
            self.logger.info(f"Webhook received from {source}: {response_id}")
    
    def log_webhook_processed(self, source: str, response_id: str, status: str, user_id: Optional[str] = None):
        """Log webhook processing result"""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(
                "webhook_processed",
                source=source,
                response_id=response_id,
                status=status,
                user_id=user_id,
                action="webhook_processed",
                webhook_status=status
            )
        else:
            self.logger.info(f"Webhook processed {source}/{response_id}: {status}")
    
    def log_dashboard_created(self, response_id: str, user_id: str, dashboard_url: str):
        """Log dashboard creation"""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(
                "dashboard_created",
                response_id=response_id,
                user_id=user_id,
                dashboard_url=dashboard_url,
                action="dashboard_created"
            )
        else:
            self.logger.info(f"Dashboard created for user {user_id}: {dashboard_url}")
    
    def log_user_registered(self, user_id: str, email: str):
        """Log user registration"""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(
                "user_registered",
                user_id=user_id,
                email=email,
                action="user_registered"
            )
        else:
            self.logger.info(f"User registered: {email}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context"""
        context = context or {}
        
        if STRUCTLOG_AVAILABLE:
            self.logger.error(
                "application_error",
                error=str(error),
                error_type=type(error).__name__,
                **context
            )
        else:
            self.logger.error(f"Error: {error}", extra=context)
        
        # Report to Google Cloud Error Reporting in production
        if self.error_client:
            try:
                self.error_client.report_exception()
            except Exception:
                pass

# Global monitor instance
monitor = FormFlowMonitor()

def capture_exception(exception: Exception, extra_data: dict = None):
    """Capture and report exceptions"""
    if settings.SENTRY_DSN and SENTRY_AVAILABLE:
        with sentry_sdk.configure_scope() as scope:
            if extra_data:
                for key, value in extra_data.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
    else:
        monitor.log_error(exception, extra_data)

def health_check() -> Dict[str, Any]:
    """Application health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "formflow-backend",
        "version": getattr(settings, 'VERSION', '1.0.0')
    }