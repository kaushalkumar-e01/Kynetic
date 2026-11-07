from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health status: healthy, degraded, or unhealthy")
    app_name: str = Field(..., description="Application name")
    environment: str = Field(..., description="Runtime environment")
    version: str = Field("0.1.0", description="API version")
    database_connected: bool = Field(..., description="Database connection health")
    database_type: str = Field("sqlite", description="Underlying database engine")
    gemini_configured: bool = Field(False, description="Whether Google Gemini API key is configured")
    ai_provider_mode: str = Field("deterministic-fallback", description="Active AI provider mode: live-gemini or deterministic-fallback")
    ai_model: Optional[str] = Field(None, description="Active AI model identifier if configured")
    configuration_notice: Optional[str] = Field(None, description="Guidance for developer environment setup")
    active_questions_count: int = Field(0, description="Total active questions in the question bank")
    timestamp: datetime = Field(..., description="Current UTC timestamp")

