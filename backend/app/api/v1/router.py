from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    profile,
    workspace,
    resumes,
    skills,
    assessments,
    projects,
    integrations,
    goals,
    placement,
    roadmaps,
    assistant,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(workspace.router, tags=["Workspace"])
api_router.include_router(resumes.router, tags=["Resumes"])
api_router.include_router(skills.router, tags=["Skills & Capabilities"])
api_router.include_router(assessments.router, tags=["Assessments"])
api_router.include_router(projects.router, tags=["Projects"])
api_router.include_router(integrations.router, tags=["Integrations"])
api_router.include_router(goals.router, tags=["Goals"])
api_router.include_router(placement.router, tags=["Placement Matching"])
api_router.include_router(roadmaps.router, tags=["Roadmaps"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
