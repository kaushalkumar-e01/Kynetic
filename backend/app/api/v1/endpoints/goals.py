from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse

router = APIRouter()


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new career or learning goal",
)
def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = Goal(
        user_id=current_user.id,
        goal_type=payload.goal_type,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        status="active",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.get(
    "/goals",
    response_model=List[GoalResponse],
    summary="List authenticated user's goals",
)
def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(desc(Goal.created_at))
        .all()
    )
    return [GoalResponse.model_validate(g) for g in goals]


@router.get(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Get goal details",
)
def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(Goal).filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        raise NotFoundException("Goal not found or access denied.")
    return GoalResponse.model_validate(goal)


@router.patch(
    "/goals/{goal_id}",
    response_model=GoalResponse,
    summary="Update goal status or details",
)
def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(Goal).filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        raise NotFoundException("Goal not found or access denied.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, val)

    db.commit()
    db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.delete(
    "/goals/{goal_id}",
    summary="Delete a goal",
)
def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(Goal).filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        raise NotFoundException("Goal not found or access denied.")

    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully."}

