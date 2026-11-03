from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserProfile
from app.models.activity import UserActivity
from app.schemas.profile import UserProfileResponse, UserProfileUpdate

router = APIRouter()


@router.get(
    "",
    response_model=UserProfileResponse,
    summary="Get authenticated user's profile",
)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create empty profile if not yet created
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return UserProfileResponse.model_validate(profile)


@router.patch(
    "",
    response_model=UserProfileResponse,
    summary="Update authenticated user's profile",
)
def update_user_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    activity = UserActivity(
        user_id=current_user.id,
        activity_type="profile_updated",
        details={"updated_fields": list(update_data.keys())},
    )
    db.add(activity)

    db.commit()
    db.refresh(profile)
    return UserProfileResponse.model_validate(profile)

