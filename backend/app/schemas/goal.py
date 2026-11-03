from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    goal_type: str = Field("placement", description="placement, career, project, or learning")
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    target_date: Optional[str] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None


class GoalResponse(BaseModel):
    id: str
    user_id: str
    goal_type: str
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobMatchCreate(BaseModel):
    role_title: str = Field(..., max_length=255, description="Target job position (e.g. Full Stack Engineer)")
    job_description: str = Field(..., min_length=20, description="Job description or requirements text")
    goal_id: Optional[str] = None
    source_reference: Optional[str] = None


class SkillMatchItem(BaseModel):
    skill: str
    category: str
    status: str = Field(..., description="matched, partial, or missing")
    user_score: float = 0.0
    evidence_types: List[str] = []


class JobMatchResponse(BaseModel):
    id: str
    user_id: str
    goal_id: Optional[str] = None
    role_title: str
    estimated_score: float
    extracted_requirements: Dict[str, Any] = Field(default_factory=dict)
    match_breakdown: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True

