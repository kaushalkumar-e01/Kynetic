from app.api.v1.endpoints.profile import get_user_profile
from app.api.v1.endpoints.workspace import get_workspace_summary, get_user_activities
from app.models.user import User, UserProfile
from app.models.project import Project
from app.models.goal import Goal
from app.models.activity import UserActivity
from app.core.security import get_password_hash


def test_user_workspace_and_profile_isolation(db_session):
    # 1. Create User A
    user_a = User(
        email="alice@example.com",
        password_hash=get_password_hash("password_alice"),
        account_status="active",
    )
    db_session.add(user_a)
    db_session.flush()

    profile_a = UserProfile(
        user_id=user_a.id,
        display_name="Alice Wonderland",
        headline="Senior AI Researcher",
    )
    project_a = Project(
        user_id=user_a.id,
        name="Alice Confidential LLM System",
        source_type="manual",
    )
    goal_a = Goal(
        user_id=user_a.id,
        goal_type="placement",
        title="Staff ML Engineer",
    )
    activity_a = UserActivity(
        user_id=user_a.id,
        activity_type="alice_private_action",
    )
    db_session.add_all([profile_a, project_a, goal_a, activity_a])

    # 2. Create User B
    user_b = User(
        email="bob@example.com",
        password_hash=get_password_hash("password_bob"),
        account_status="active",
    )
    db_session.add(user_b)
    db_session.flush()

    profile_b = UserProfile(
        user_id=user_b.id,
        display_name="Bob Builder",
        headline="Frontend Specialist",
    )
    activity_b = UserActivity(
        user_id=user_b.id,
        activity_type="bob_public_action",
    )
    db_session.add_all([profile_b, activity_b])
    db_session.commit()

    # 3. Test Profile Isolation
    bob_profile = get_user_profile(current_user=user_b, db=db_session)
    assert bob_profile.user_id == user_b.id
    assert bob_profile.display_name == "Bob Builder"
    assert bob_profile.display_name != "Alice Wonderland"

    alice_profile = get_user_profile(current_user=user_a, db=db_session)
    assert alice_profile.user_id == user_a.id
    assert alice_profile.display_name == "Alice Wonderland"

    # 4. Test Workspace Summary Isolation
    bob_summary = get_workspace_summary(current_user=user_b, db=db_session)
    assert bob_summary.user.email == "bob@example.com"
    # Bob should have 0 projects and 0 goals
    assert bob_summary.projects_count == 0
    assert bob_summary.goals_count == 0
    assert len(bob_summary.recent_activities) == 1
    assert bob_summary.recent_activities[0].activity_type == "bob_public_action"

    alice_summary = get_workspace_summary(current_user=user_a, db=db_session)
    assert alice_summary.projects_count == 1
    assert alice_summary.goals_count == 1
    assert any(a.activity_type == "alice_private_action" for a in alice_summary.recent_activities)

    # 5. Test Activity Log Isolation
    bob_activities = get_user_activities(current_user=user_b, db=db_session)
    assert len(bob_activities) == 1
    assert bob_activities[0].activity_type == "bob_public_action"
    assert all(a.activity_type != "alice_private_action" for a in bob_activities)

