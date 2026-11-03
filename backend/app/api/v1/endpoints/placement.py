from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.goal import JobMatch
from app.schemas.goal import JobMatchCreate, JobMatchResponse
from app.services.matching_service import matching_service

router = APIRouter()


@router.post(
    "/placement/matches",
    response_model=JobMatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Match target role and job description against capability profile",
)
def create_job_match(
    payload: JobMatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match_record = matching_service.match_job_description(
        user_id=current_user.id,
        role_title=payload.role_title,
        job_description=payload.job_description,
        goal_id=payload.goal_id,
        source_reference=payload.source_reference,
        db=db,
    )
    return JobMatchResponse.model_validate(match_record)


@router.get(
    "/placement/matches",
    response_model=List[JobMatchResponse],
    summary="List saved job matches",
)
def list_job_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    matches = (
        db.query(JobMatch)
        .filter(JobMatch.user_id == current_user.id)
        .order_by(desc(JobMatch.created_at))
        .all()
    )
    return [JobMatchResponse.model_validate(m) for m in matches]


@router.get(
    "/placement/matches/{match_id}",
    response_model=JobMatchResponse,
    summary="Get job match details and skill gap breakdown",
)
def get_job_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match_record = db.query(JobMatch).filter_by(id=match_id, user_id=current_user.id).first()
    if not match_record:
        raise NotFoundException("Job match record not found or access denied.")
    return JobMatchResponse.model_validate(match_record)

