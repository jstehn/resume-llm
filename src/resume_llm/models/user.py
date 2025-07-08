"""User-related Pydantic models."""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """User creation model."""
    pass


class UserUpdate(BaseModel):
    """User update model."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Any]] = None


class User(UserBase):
    """User response model."""
    id: int
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithStats(User):
    """User model with statistics."""
    resume_count: int = 0
    application_count: int = 0
    active_conversations: int = 0


class APIKeyUpdate(BaseModel):
    """Model for updating API keys."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    class Config:
        extra = "forbid"  # Don't allow additional fields
