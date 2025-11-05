"""
Authentication API Routes
OAuth2 and authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    Token, OAuthCallback, UserResponse, GoogleUserInfo
)
from app.services.auth import (
    get_google_authorization_url,
    exchange_code_for_token,
    get_google_user_info,
    create_access_token,
    encrypt_token
)
from app.middleware.auth import get_current_active_user

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth2 login flow"""
    authorization_url, state = get_google_authorization_url()
    return {
        "authorization_url": authorization_url,
        "state": state
    }


@router.post("/google/callback")
async def google_callback(
    callback: OAuthCallback,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth2 callback"""
    try:
        # Exchange code for credentials
        credentials = exchange_code_for_token(callback.code)
        
        # Get user info from Google
        google_user_info = get_google_user_info(credentials)
        
        # Find or create user
        user = db.query(User).filter(User.email == google_user_info.email).first()
        
        if user:
            # Update existing user
            user.name = google_user_info.name
            user.picture = google_user_info.picture
            user.google_id = google_user_info.id
            user.access_token = encrypt_token(credentials.token)
            user.refresh_token = encrypt_token(credentials.refresh_token) if credentials.refresh_token else None
            user.token_expires_at = datetime.fromtimestamp(credentials.expiry) if credentials.expiry else None
            user.last_login = datetime.utcnow()
        else:
            # Create new user (default role: USER)
            user = User(
                email=google_user_info.email,
                name=google_user_info.name,
                picture=google_user_info.picture,
                google_id=google_user_info.id,
                access_token=encrypt_token(credentials.token),
                refresh_token=encrypt_token(credentials.refresh_token) if credentials.refresh_token else None,
                token_expires_at=datetime.fromtimestamp(credentials.expiry) if credentials.expiry else None,
                role=UserRole.USER,
                is_active=True,
                last_login=datetime.utcnow()
            )
            db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user (invalidate token on client side)"""
    # In a full implementation, you might want to blacklist the token
    # For now, we'll just return success
    return {"message": "Logged out successfully"}

