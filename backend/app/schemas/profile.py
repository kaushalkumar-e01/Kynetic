from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    display_name: Optional[str] = None
    headline: Optional[str] = None
    education_summary: Optional[str] = None
    experience_summary: Optional[str] = None
    preferred_domains: List[str] = Field(default_factory=list)
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    headline: Optional[str] = Field(None, max_length=255)
    education_summary: Optional[str] = None
    experience_summary: Optional[str] = None
    preferred_domains: Optional[List[str]] = None
    learning_preferences: Optional[Dict[str, Any]] = None

