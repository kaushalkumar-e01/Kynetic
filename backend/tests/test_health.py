from app.main import app
from app.api.v1.endpoints.health import get_health
from app.core.config import settings
from app.schemas.health import HealthResponse


def test_health_endpoint_logic():
    response = get_health()
    assert isinstance(response, HealthResponse)
    assert response.status in ["healthy", "degraded"]
    assert response.app_name == settings.APP_NAME
    assert response.environment == settings.APP_ENV
    assert response.version == "0.1.0"
    assert isinstance(response.database_connected, bool)
    assert response.timestamp is not None


def test_app_routes_registered():
    route_paths = [route.path for route in app.routes]
    assert "/api/v1/health" in route_paths
    assert "/health" in route_paths
    assert "/" in route_paths
    assert "/docs" in route_paths
    assert f"{settings.API_V1_PREFIX}/openapi.json" in route_paths
    assert "/api/v1/auth/register" in route_paths
    assert "/api/v1/auth/login" in route_paths
    assert "/api/v1/auth/logout" in route_paths
    assert "/api/v1/auth/me" in route_paths
    assert "/api/v1/profile" in route_paths
    assert "/api/v1/workspace/summary" in route_paths
    assert "/api/v1/activity" in route_paths
    assert "/api/v1/settings" in route_paths
    assert "/api/v1/resumes" in route_paths
    assert "/api/v1/resumes/{resume_id}" in route_paths
    assert "/api/v1/resumes/{resume_id}/analyze" in route_paths
    assert "/api/v1/skills" in route_paths
    assert "/api/v1/capabilities" in route_paths
    assert "/api/v1/evidence" in route_paths
    assert "/api/v1/assessment-topics" in route_paths
    assert "/api/v1/questions" in route_paths
    assert "/api/v1/assessments" in route_paths
    assert "/api/v1/assessments/{assessment_id}/answers" in route_paths
    assert "/api/v1/assessments/{assessment_id}/code-submissions" in route_paths
    assert "/api/v1/assessments/{assessment_id}/results" in route_paths
    assert "/api/v1/assessment-attempts" in route_paths
    assert "/api/v1/projects" in route_paths
    assert "/api/v1/projects/{project_id}" in route_paths
    assert "/api/v1/projects/{project_id}/analyze" in route_paths
    assert "/api/v1/integrations/github/connect" in route_paths
    assert "/api/v1/integrations/github/repositories" in route_paths
    assert "/api/v1/goals" in route_paths
    assert "/api/v1/placement/matches" in route_paths
    assert "/api/v1/roadmaps" in route_paths
    assert "/api/v1/roadmaps/{roadmap_id}/milestones" in route_paths
    assert "/api/v1/assistant/messages" in route_paths
    assert "/api/v1/assistant/conversations" in route_paths


def test_cors_configuration():
    origins = settings.cors_origins_list
    assert settings.FRONTEND_ORIGIN in origins
    assert "http://localhost:3000" in origins
