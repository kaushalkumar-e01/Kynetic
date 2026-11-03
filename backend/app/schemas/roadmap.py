from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MilestoneCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    ordering: int = Field(0, ge=0)
    due_date: Optional[str] = None


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    resources: Optional[List[Dict[str, Any]]] = None
    ordering: Optional[int] = None
    status: Optional[str] = Field(None, description="pending, in_progress, completed")
    due_date: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: str
    roadmap_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    resources: List[Dict[str, Any]] = []
    ordering: int
    status: str
    due_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoadmapCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    goal_id: Optional[str] = None
    target_skills: List[str] = Field(default_factory=list, description="Target skills to master in this roadmap")


class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="active, completed, paused")


class RoadmapResponse(BaseModel):
    id: str
    user_id: str
    goal_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    milestones: List[MilestoneResponse] = []
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True

