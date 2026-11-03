from app.api.v1.endpoints.profile import get_user_profile, update_user_profile
from app.schemas.profile import UserProfileUpdate
from app.models.user import User
from app.models.activity import UserActivity
from app.core.security import get_password_hash


def test_profile_retrieval_and_creation(db_session):
    user = User(
        email="profile_user@example.com",
        password_hash=get_password_hash("password123"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Calling get_user_profile should auto-initialize profile if missing
    profile_response = get_user_profile(current_user=user, db=db_session)
    assert profile_response.user_id == user.id
    assert profile_response.display_name is None


def test_profile_update(db_session):
    user = User(
        email="update_profile@example.com",
        password_hash=get_password_hash("password123"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    update_payload = UserProfileUpdate(
        display_name="Ketan Developer",
        headline="AI & Backend Architect",
        preferred_domains=["AI", "Distributed Systems"],
        learning_preferences={"pace": "intensive", "daily_minutes": 60},
    )

    updated = update_user_profile(payload=update_payload, current_user=user, db=db_session)

    assert updated.display_name == "Ketan Developer"
    assert updated.headline == "AI & Backend Architect"
    assert "AI" in updated.preferred_domains
    assert updated.learning_preferences["daily_minutes"] == 60

    # Verify audit activity created
    activity = (
        db_session.query(UserActivity)
        .filter_by(user_id=user.id, activity_type="profile_updated")
        .first()
    )
    assert activity is not None

