"""
Secure Storage Service
TASK-040: Secure credential storage with encryption
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.encryption import get_encryption_service
import logging

logger = logging.getLogger(__name__)


class SecureStorageService:
    """Service for securely storing and retrieving encrypted credentials"""
    
    def __init__(self, db: Session):
        """Initialize secure storage service"""
        self.db = db
        self.encryption = get_encryption_service()
    
    def store_credentials(
        self,
        user: User,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expires_at: Optional[datetime] = None
    ) -> User:
        """
        Store encrypted credentials for user
        
        Args:
            user: User to store credentials for
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            token_expires_at: Token expiration timestamp
            
        Returns:
            Updated user object
        """
        from datetime import datetime
        
        # Encrypt tokens
        user.access_token = self.encryption.encrypt(access_token)
        if refresh_token:
            user.refresh_token = self.encryption.encrypt(refresh_token)
        if token_expires_at:
            user.token_expires_at = token_expires_at
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Stored encrypted credentials for user {user.id}")
        
        return user
    
    def get_access_token(self, user: User) -> Optional[str]:
        """
        Retrieve and decrypt access token
        
        Args:
            user: User to get token for
            
        Returns:
            Decrypted access token or None
        """
        if not user.access_token:
            return None
        
        try:
            return self.encryption.decrypt(user.access_token)
        except Exception as e:
            logger.error(f"Error decrypting access token for user {user.id}: {e}")
            return None
    
    def get_refresh_token(self, user: User) -> Optional[str]:
        """
        Retrieve and decrypt refresh token
        
        Args:
            user: User to get token for
            
        Returns:
            Decrypted refresh token or None
        """
        if not user.refresh_token:
            return None
        
        try:
            return self.encryption.decrypt(user.refresh_token)
        except Exception as e:
            logger.error(f"Error decrypting refresh token for user {user.id}: {e}")
            return None
    
    def clear_credentials(self, user: User) -> User:
        """
        Clear all stored credentials
        
        Args:
            user: User to clear credentials for
            
        Returns:
            Updated user object
        """
        user.access_token = None
        user.refresh_token = None
        user.token_expires_at = None
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"Cleared credentials for user {user.id}")
        
        return user
    
    def is_token_valid(self, user: User) -> bool:
        """
        Check if stored token is still valid
        
        Args:
            user: User to check token for
            
        Returns:
            True if token exists and is not expired
        """
        if not user.access_token or not user.token_expires_at:
            return False
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < user.token_expires_at


def get_secure_storage_service(db: Session) -> SecureStorageService:
    """Get secure storage service instance"""
    return SecureStorageService(db)

