from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
from app.models.user import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for JWT token management"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token (30 days expiry)"""
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    def create_reset_token(user_id: str) -> str:
        """Create password reset token (15 minutes expiry)"""
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode = {"sub": user_id, "exp": expire, "type": "reset"}
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def create_verification_token(user_id: str) -> str:
        """Create email verification token (24 hours expiry)"""
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = {"sub": user_id, "exp": expire, "type": "verification"}
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.verify_password(password):
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        google_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        is_verified: bool = False
    ) -> User:
        """Create a new user"""
        user_data = {
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "is_verified": is_verified
        }
        
        if password:
            user_data["hashed_password"] = User.hash_password(password)
        
        if google_id:
            user_data["google_id"] = google_id
            user_data["oauth_provider"] = "google"
            user_data["is_verified"] = True  # Google accounts are pre-verified
        
        user = User(**user_data)
        db.add(user)
        db.flush()  # Use flush instead of commit to keep transaction open
        db.refresh(user)
        
        logger.info(f"Created new user: {email} (ID: {user.id})")
        return user
    
    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> Optional[str]:
        """Create new access token from refresh token"""
        payload = AuthService.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user or not user.is_active:
            return None
        
        # Create new access token
        return AuthService.create_access_token({"sub": user_id})