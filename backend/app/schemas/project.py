from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, computed_field


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    source_type: str = Field("manual", description="Source type: 'manual' or 'github'")
    repository_url: Optional[str] = None
    technologies: Optional[List[str]] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = None
    technologies: Optional[List[str]] = None


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
    source_snapshot: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    @computed_field
    @property
    def major_features(self) -> List[str]:
        if self.source_snapshot and isinstance(self.source_snapshot, dict):
            return self.source_snapshot.get("major_features", [])
        return []

    @computed_field
    @property
    def technical_strengths(self) -> List[str]:
        if self.source_snapshot and isinstance(self.source_snapshot, dict):
            return self.source_snapshot.get("technical_strengths", [])
        return []

    @computed_field
    @property
    def inspected_files(self) -> List[str]:
        if self.source_snapshot and isinstance(self.source_snapshot, dict):
            return self.source_snapshot.get("inspected_files", [])
        return []

    @computed_field
    @property
    def model_metadata(self) -> Dict[str, Any]:
        if self.source_snapshot and isinstance(self.source_snapshot, dict):
            return self.source_snapshot.get("model_metadata", {})
        return {}

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    source_type: str
    repository_url: Optional[str] = None
    access_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    latest_analysis: Optional[ProjectAnalysisResponse] = None

    @computed_field
    @property
    def technologies(self) -> List[str]:
        if self.access_metadata and isinstance(self.access_metadata, dict):
            return self.access_metadata.get("technologies", [])
        return []

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
    technologies: Optional[List[str]] = Field(default_factory=list)
