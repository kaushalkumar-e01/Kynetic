from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.auth import UserResponse
from app.schemas.profile import UserProfileResponse
from app.schemas.common import UTCDateTime


class ActivityResponse(BaseModel):
    id: str
    activity_type: str
    related_record_type: Optional[str] = None
    related_record_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: UTCDateTime

    class Config:
        from_attributes = True


class WorkspaceSummaryResponse(BaseModel):
    user: UserResponse
    profile: Optional[UserProfileResponse] = None
    resumes_count: int = 0
    projects_count: int = 0
    assessments_count: int = 0
    goals_count: int = 0
    roadmaps_count: int = 0
    recent_activities: List[ActivityResponse] = Field(default_factory=list)
    recent_goals: List[Dict[str, Any]] = Field(default_factory=list)
    active_roadmap: Optional[Dict[str, Any]] = None


class UserSettingsResponse(BaseModel):
    email: str
    account_status: str
    learning_preferences: Dict[str, Any] = Field(default_factory=dict)


class UserSettingsUpdate(BaseModel):
    learning_preferences: Optional[Dict[str, Any]] = None

