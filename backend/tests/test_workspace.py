from app.api.v1.endpoints.workspace import (
    get_workspace_summary,
    get_user_activities,
    get_user_settings,
    update_user_settings,
)
from app.schemas.workspace import UserSettingsUpdate
from app.models.user import User, UserProfile
from app.models.project import Project
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.activity import UserActivity
from app.core.security import get_password_hash


def test_workspace_summary_aggregation(db_session):
    user = User(
        email="workspace_test@example.com",
        password_hash=get_password_hash("password123"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = UserProfile(user_id=user.id, display_name="Workspace Tester")
    project = Project(user_id=user.id, name="Test Project", source_type="manual")
    goal = Goal(user_id=user.id, goal_type="placement", title="Targeting Software Engineer")
    roadmap = Roadmap(user_id=user.id, title="Backend Mastery", status="active")
    activity = UserActivity(user_id=user.id, activity_type="custom_event")

    db_session.add_all([profile, project, goal, roadmap, activity])
    db_session.commit()

    summary = get_workspace_summary(current_user=user, db=db_session)

    assert summary.user.email == "workspace_test@example.com"
    assert summary.profile.display_name == "Workspace Tester"
    assert summary.projects_count == 1
    assert summary.goals_count == 1
    assert summary.roadmaps_count == 1
    assert summary.active_roadmap is not None
    assert summary.active_roadmap["title"] == "Backend Mastery"
    assert len(summary.recent_activities) >= 1


def test_activity_log(db_session):
    user = User(
        email="activity_user@example.com",
        password_hash=get_password_hash("password123"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    for i in range(5):
        db_session.add(UserActivity(user_id=user.id, activity_type=f"test_activity_{i}"))
    db_session.commit()

    activities = get_user_activities(limit=10, current_user=user, db=db_session)
    assert len(activities) == 5


def test_settings_retrieval_and_update(db_session):
    user = User(
        email="settings_user@example.com",
        password_hash=get_password_hash("password123"),
        account_status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Initial settings
    settings = get_user_settings(current_user=user, db=db_session)
    assert settings.email == "settings_user@example.com"

    # Update settings
    updated = update_user_settings(
        payload=UserSettingsUpdate(learning_preferences={"theme": "dark", "reminder": True}),
        current_user=user,
        db=db_session,
    )
    assert updated.learning_preferences["theme"] == "dark"
    assert updated.learning_preferences["reminder"] is True

