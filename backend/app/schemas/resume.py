from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ResumeAnalysisResponse(BaseModel):
    id: str
    user_id: str
    resume_id: str
    status: str
    extracted_profile: Optional[Dict[str, Any]] = None
    strengths: List[str] = []
    suggestions: List[str] = []
    model_metadata: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    original_filename: str
    mime_type: str
    file_size: int
    version_label: Optional[str] = None
    status: str
    created_at: datetime
    analysis: Optional[ResumeAnalysisResponse] = None

    class Config:
        from_attributes = True

