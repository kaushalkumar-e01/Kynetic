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

    q_count = 0
    if is_db_connected:
        try:
            from app.db.session import SessionLocal
            from app.models.assessment import Question
            with SessionLocal() as db:
                q_count = db.query(Question).filter(Question.is_active.is_(True)).count()
        except Exception:
            q_count = 0

    response_data = HealthResponse(
        status=status_str,
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        database_connected=is_db_connected,
        database_type="sqlite" if settings.effective_database_url.startswith("sqlite") else "postgresql",
        gemini_configured=bool(settings.effective_gemini_api_key),
        active_questions_count=q_count,
        timestamp=datetime.now(timezone.utc),
    )

    return response_data

