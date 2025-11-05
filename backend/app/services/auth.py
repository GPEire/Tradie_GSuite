"""
Authentication Service
OAuth2 and JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from app.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import GoogleUserInfo

# Password hashing context (for future use if needed)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.secret_key or "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days for extension usage


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_google_oauth_flow() -> Flow:
    """Create Google OAuth2 flow"""
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=settings.gmail_scopes.split(","),
        redirect_uri=settings.google_redirect_uri
    )
    
    return flow


def get_google_authorization_url() -> tuple[str, str]:
    """Get Google OAuth authorization URL"""
    flow = get_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state


def exchange_code_for_token(code: str) -> Credentials:
    """Exchange authorization code for access token"""
    flow = get_google_oauth_flow()
    flow.fetch_token(code=code)
    return flow.credentials


def get_google_user_info(credentials: Credentials) -> GoogleUserInfo:
    """Get user info from Google using credentials"""
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    return GoogleUserInfo(
        id=user_info.get('id'),
        email=user_info.get('email'),
        verified_email=user_info.get('verified_email', False),
        name=user_info.get('name', ''),
        picture=user_info.get('picture'),
        given_name=user_info.get('given_name'),
        family_name=user_info.get('family_name'),
    )


def encrypt_token(token: str) -> str:
    """Encrypt token for storage (simple base64 encoding for MVP)"""
    # In production, use proper encryption (AES-256)
    import base64
    return base64.b64encode(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt token from storage"""
    import base64
    return base64.b64decode(encrypted_token.encode()).decode()

