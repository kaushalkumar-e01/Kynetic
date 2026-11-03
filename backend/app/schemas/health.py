from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health status: healthy, degraded, or unhealthy")
    app_name: str = Field(..., description="Application name")
    environment: str = Field(..., description="Runtime environment")
    version: str = Field("0.1.0", description="API version")
    database_connected: bool = Field(..., description="Database connection health")
    timestamp: datetime = Field(..., description="Current UTC timestamp")

