from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserProfile
from app.models.resume import Resume
from app.models.project import Project
from app.models.assessment import Assessment
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.activity import UserActivity
from app.schemas.auth import UserResponse
from app.schemas.profile import UserProfileResponse
from app.schemas.workspace import (
    ActivityResponse,
    WorkspaceSummaryResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)

router = APIRouter()


@router.get(
    "/workspace/summary",
    response_model=WorkspaceSummaryResponse,
    summary="Get user personalized workspace summary",
)
def get_workspace_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    resumes_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    projects_count = db.query(Project).filter(Project.user_id == current_user.id).count()
    assessments_count = db.query(Assessment).filter(Assessment.user_id == current_user.id).count()
    goals_count = db.query(Goal).filter(Goal.user_id == current_user.id).count()
    roadmaps_count = db.query(Roadmap).filter(Roadmap.user_id == current_user.id).count()

    recent_activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == current_user.id)
        .order_by(desc(UserActivity.created_at))
        .limit(10)
        .all()
    )

    recent_goals = (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(desc(Goal.created_at))
        .limit(5)
        .all()
    )

    active_roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == current_user.id, Roadmap.status == "active")
        .order_by(desc(Roadmap.updated_at))
        .first()
    )

    return WorkspaceSummaryResponse(
        user=UserResponse.model_validate(current_user),
        profile=UserProfileResponse.model_validate(profile) if profile else None,
        resumes_count=resumes_count,
        projects_count=projects_count,
        assessments_count=assessments_count,
        goals_count=goals_count,
        roadmaps_count=roadmaps_count,
        recent_activities=[ActivityResponse.model_validate(a) for a in recent_activities],
        recent_goals=[
            {"id": g.id, "title": g.title, "goal_type": g.goal_type, "status": g.status}
            for g in recent_goals
        ],
        active_roadmap={"id": active_roadmap.id, "title": active_roadmap.title, "status": active_roadmap.status}
        if active_roadmap
        else None,
    )


@router.get(
    "/activity",
    response_model=List[ActivityResponse],
    summary="Get user activity log",
)
def get_user_activities(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actual_limit = limit if isinstance(limit, int) else 20
    activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == current_user.id)
        .order_by(desc(UserActivity.created_at))
        .limit(actual_limit)
        .all()
    )
    return [ActivityResponse.model_validate(a) for a in activities]


@router.get(
    "/settings",
    response_model=UserSettingsResponse,
    summary="Get user account settings",
)
def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    return UserSettingsResponse(
        email=current_user.email,
        account_status=current_user.account_status,
        learning_preferences=profile.learning_preferences if profile and profile.learning_preferences else {},
    )


@router.patch(
    "/settings",
    response_model=UserSettingsResponse,
    summary="Update user settings",
)
def update_user_settings(
    payload: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if payload.learning_preferences is not None:
        profile.learning_preferences = payload.learning_preferences

    activity = UserActivity(
        user_id=current_user.id,
        activity_type="settings_updated",
    )
    db.add(activity)

    db.commit()
    db.refresh(profile)

    return UserSettingsResponse(
        email=current_user.email,
        account_status=current_user.account_status,
        learning_preferences=profile.learning_preferences or {},
    )
