from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.project import Project, ProjectAnalysis
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectAnalysisResponse,
)
from app.services.project_service import project_service

router = APIRouter()


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new manual or GitHub project",
)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    access_metadata = {}
    if payload.technologies:
        access_metadata["technologies"] = payload.technologies

    project = Project(
        user_id=current_user.id,
        name=payload.name,
        description=payload.description,
        source_type=payload.source_type,
        repository_url=payload.repository_url,
        access_metadata=access_metadata,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    summary="List authenticated user's projects",
)
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(desc(Project.created_at))
        .all()
    )
    results = []
    for p in projects:
        dto = ProjectResponse.model_validate(p)
        latest_analysis = (
            db.query(ProjectAnalysis)
            .filter_by(project_id=p.id)
            .order_by(desc(ProjectAnalysis.created_at))
            .first()
        )
        if latest_analysis:
            dto.latest_analysis = ProjectAnalysisResponse.model_validate(latest_analysis)
        results.append(dto)
    return results


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        raise NotFoundException("Project not found or access denied.")

    dto = ProjectResponse.model_validate(project)
    latest_analysis = (
        db.query(ProjectAnalysis)
        .filter_by(project_id=project.id)
        .order_by(desc(ProjectAnalysis.created_at))
        .first()
    )
    if latest_analysis:
        dto.latest_analysis = ProjectAnalysisResponse.model_validate(latest_analysis)
    return dto


@router.patch(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    summary="Update project metadata",
)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        raise NotFoundException("Project not found or access denied.")

    update_dict = payload.model_dump(exclude_unset=True)
    if "technologies" in update_dict:
        techs = update_dict.pop("technologies")
        meta = dict(project.access_metadata or {})
        meta["technologies"] = techs
        project.access_metadata = meta

    for field, val in update_dict.items():
        setattr(project, field, val)

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete(
    "/projects/{project_id}",
    summary="Delete a project and its analyses",
)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        raise NotFoundException("Project not found or access denied.")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully."}


@router.post(
    "/projects/{project_id}/analyze",
    response_model=ProjectAnalysisResponse,
    summary="Trigger analysis of project repository/description",
)
def analyze_project_endpoint(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = project_service.analyze_project(
        project_id=project_id,
        user_id=current_user.id,
        db=db,
    )
    return ProjectAnalysisResponse.model_validate(analysis)


@router.get(
    "/projects/{project_id}/analyses",
    response_model=List[ProjectAnalysisResponse],
    summary="Get all analyses for a project",
)
def get_project_analyses(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter_by(id=project_id, user_id=current_user.id).first()
    if not project:
        raise NotFoundException("Project not found or access denied.")

    analyses = (
        db.query(ProjectAnalysis)
        .filter_by(project_id=project_id, user_id=current_user.id)
        .order_by(desc(ProjectAnalysis.created_at))
        .all()
    )
    return [ProjectAnalysisResponse.model_validate(a) for a in analyses]


@router.get(
    "/project-analyses/{analysis_id}",
    response_model=ProjectAnalysisResponse,
    summary="Get specific project analysis by ID",
)
def get_project_analysis_by_id(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.query(ProjectAnalysis).filter_by(id=analysis_id, user_id=current_user.id).first()
    if not analysis:
        raise NotFoundException("Project analysis not found or access denied.")

    return ProjectAnalysisResponse.model_validate(analysis)
