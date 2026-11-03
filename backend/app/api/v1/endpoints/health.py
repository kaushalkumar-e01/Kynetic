from datetime import datetime, timezone
from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns API status, environment information, and database connectivity.",
)
def get_health():
    is_db_connected = check_db_connection()
    status_str = "healthy" if is_db_connected else "degraded"

    response_data = HealthResponse(
        status=status_str,
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        database_connected=is_db_connected,
        timestamp=datetime.now(timezone.utc),
    )

    # If DB is not connected, return 200 with degraded status or 503 if required.
    # Typically 200 with degraded allows frontend/monitors to distinguish API up vs dependencies down.
    return response_data

