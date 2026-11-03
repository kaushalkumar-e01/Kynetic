from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SkillResponse(BaseModel):
    id: str
    canonical_name: str
    category: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class EvidenceRecordResponse(BaseModel):
    id: str
    user_id: str
    skill_id: str
    source_type: str
    source_record_id: Optional[str] = None
    summary: str
    confidence: float
    quality_metadata: Dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UserCapabilityResponse(BaseModel):
    id: str
    user_id: str
    skill_id: str
    skill_name: Optional[str] = None
    category: Optional[str] = None
    estimated_band: str
    score: float
    confidence: float
    evidence_count: int
    last_evaluated_at: datetime

    class Config:
        from_attributes = True


class CreateEvidenceRequest(BaseModel):
    skill_name: str = Field(..., max_length=100)
    category: str = Field("concept", max_length=50)
    summary: str = Field(..., description="Summary of confirmed skill evidence")
    confidence: float = Field(0.7, ge=0.0, le=1.0)

