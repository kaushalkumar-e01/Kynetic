from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    source_type: str = Field("manual", description="Source type: 'manual' or 'github'")
    repository_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = None


class ProjectAnalysisResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    status: str
    purpose: Optional[str] = None
    detected_technologies: List[str] = []
    architecture_summary: Optional[str] = None
    demonstrated_skills: List[str] = []
    missing_requirements: List[str] = []
    recommendations: List[str] = []
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    source_type: str
    repository_url: Optional[str] = None
    created_at: datetime
    latest_analysis: Optional[ProjectAnalysisResponse] = None

    class Config:
        from_attributes = True


class GitHubConnectResponse(BaseModel):
    authorization_url: str
    state: str


class GitHubRepoItem(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    is_private: bool
    stargazers_count: int = 0
    updated_at: Optional[str] = None


class ImportGitHubRepoRequest(BaseModel):
    repository_url: str
    name: Optional[str] = None
    description: Optional[str] = None

