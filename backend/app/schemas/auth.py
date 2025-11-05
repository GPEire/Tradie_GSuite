"""
Authentication Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None
    user_id: Optional[int] = None


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    google_id: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = None
    picture: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class OAuthCallback(BaseModel):
    """OAuth callback request"""
    code: str
    state: Optional[str] = None


class GoogleUserInfo(BaseModel):
    """Google user info from OAuth"""
    id: str
    email: str
    verified_email: bool
    name: str
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None

