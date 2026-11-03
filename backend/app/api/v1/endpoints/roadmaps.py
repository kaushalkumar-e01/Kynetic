from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.roadmap import Roadmap, RoadmapMilestone
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapResponse,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
)
from app.services.roadmap_service import roadmap_service

router = APIRouter()


@router.post(
    "/roadmaps",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate personalized learning roadmap",
)
def create_roadmap(
    payload: RoadmapCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = roadmap_service.generate_roadmap(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        goal_id=payload.goal_id,
        target_skills=payload.target_skills,
        db=db,
    )
    dto = RoadmapResponse.model_validate(roadmap)
    dto.milestones = [MilestoneResponse.model_validate(m) for m in roadmap.milestones]
    dto.progress_percentage = roadmap_service.calculate_progress(roadmap)
    return dto


@router.get(
    "/roadmaps",
    response_model=List[RoadmapResponse],
    summary="List authenticated user's roadmaps",
)
def list_roadmaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id)
        .order_by(desc(Roadmap.updated_at))
        .all()
    )
    results = []
    for r in roadmaps:
        dto = RoadmapResponse.model_validate(r)
        dto.milestones = [MilestoneResponse.model_validate(m) for m in r.milestones]
        dto.progress_percentage = roadmap_service.calculate_progress(r)
        results.append(dto)
    return results


@router.get(
    "/roadmaps/{roadmap_id}",
    response_model=RoadmapResponse,
    summary="Get roadmap details and milestone progression",
)
def get_roadmap(
    roadmap_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = db.query(Roadmap).filter_by(id=roadmap_id, user_id=current_user.id).first()
    if not roadmap:
        raise NotFoundException("Roadmap not found or access denied.")

    dto = RoadmapResponse.model_validate(roadmap)
    dto.milestones = [MilestoneResponse.model_validate(m) for m in roadmap.milestones]
    dto.progress_percentage = roadmap_service.calculate_progress(roadmap)
    return dto


@router.patch(
    "/roadmaps/{roadmap_id}",
    response_model=RoadmapResponse,
    summary="Update roadmap status or metadata",
)
def update_roadmap(
    roadmap_id: str,
    payload: RoadmapUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = db.query(Roadmap).filter_by(id=roadmap_id, user_id=current_user.id).first()
    if not roadmap:
        raise NotFoundException("Roadmap not found or access denied.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(roadmap, field, val)

    db.commit()
    db.refresh(roadmap)

    dto = RoadmapResponse.model_validate(roadmap)
    dto.milestones = [MilestoneResponse.model_validate(m) for m in roadmap.milestones]
    dto.progress_percentage = roadmap_service.calculate_progress(roadmap)
    return dto


@router.post(
    "/roadmaps/{roadmap_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new milestone to roadmap",
)
def add_milestone(
    roadmap_id: str,
    payload: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = db.query(Roadmap).filter_by(id=roadmap_id, user_id=current_user.id).first()
    if not roadmap:
        raise NotFoundException("Roadmap not found or access denied.")

    milestone = RoadmapMilestone(
        user_id=current_user.id,
        roadmap_id=roadmap.id,
        title=payload.title,
        description=payload.description,
        resources=payload.resources,
        ordering=payload.ordering or (len(roadmap.milestones) + 1),
        due_date=payload.due_date,
        status="pending",
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return MilestoneResponse.model_validate(milestone)


@router.patch(
    "/roadmaps/{roadmap_id}/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    summary="Update milestone progress and status",
)
def update_milestone(
    roadmap_id: str,
    milestone_id: str,
    payload: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    milestone = (
        db.query(RoadmapMilestone)
        .filter_by(id=milestone_id, roadmap_id=roadmap_id, user_id=current_user.id)
        .first()
    )
    if not milestone:
        raise NotFoundException("Milestone not found or access denied.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, val)

    db.commit()
    db.refresh(milestone)
    return MilestoneResponse.model_validate(milestone)

