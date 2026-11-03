from app.models.user import User
from app.models.skill import Skill, UserCapability
from app.core.security import get_password_hash
from app.schemas.goal import GoalCreate, GoalUpdate, JobMatchCreate
from app.api.v1.endpoints.goals import create_goal, list_goals, update_goal
from app.api.v1.endpoints.placement import create_job_match, get_job_match


def test_goal_crud_operations(db_session):
    user = User(email="goal_test_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    goal_req = GoalCreate(
        goal_type="placement",
        title="Land Backend Engineer Role",
        description="Targeting tier-1 product companies",
        target_date="2026-12-31",
    )
    goal_dto = create_goal(payload=goal_req, current_user=user, db=db_session)
    assert goal_dto.title == "Land Backend Engineer Role"
    assert goal_dto.status == "active"

    # Update goal
    up_req = GoalUpdate(title="Land Senior Backend Engineer Role", status="completed")
    updated = update_goal(goal_id=goal_dto.id, payload=up_req, current_user=user, db=db_session)
    assert updated.title == "Land Senior Backend Engineer Role"
    assert updated.status == "completed"

    # List goals
    all_goals = list_goals(current_user=user, db=db_session)
    assert len(all_goals) == 1


def test_placement_matching_with_capability_breakdown(db_session):
    user = User(email="matching_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    # Pre-populate user capabilities: Python (proficient 90%), SQL (partial 40%)
    skill_py = Skill(canonical_name="Python", category="language")
    skill_sql = Skill(canonical_name="SQL", category="language")
    db_session.add_all([skill_py, skill_sql])
    db_session.flush()

    cap_py = UserCapability(user_id=user.id, skill_id=skill_py.id, score=90.0, estimated_band="proficient", confidence=0.9)
    cap_sql = UserCapability(user_id=user.id, skill_id=skill_sql.id, score=40.0, estimated_band="foundational", confidence=0.7)
    db_session.add_all([cap_py, cap_sql])
    db_session.commit()
    db_session.refresh(user)

    # Job description requiring Python, SQL, Docker, and Kubernetes
    job_desc = """
    We are looking for a Senior Backend Developer.
    Requirements:
    - 3+ years experience with Python and REST API development.
    - Strong knowledge of SQL and PostgreSQL relational databases.
    - Familiarity with Docker containerization and Kubernetes orchestration.
    """
    payload = JobMatchCreate(
        role_title="Senior Backend Developer",
        job_description=job_desc,
    )
    match_dto = create_job_match(payload=payload, current_user=user, db=db_session)

    assert match_dto.role_title == "Senior Backend Developer"
    assert match_dto.estimated_score > 0.0

    breakdown = match_dto.match_breakdown
    assert breakdown["matched_count"] >= 1  # Python matched
    assert breakdown["partial_count"] >= 1  # SQL partial
    assert breakdown["missing_count"] >= 1  # Docker/Kubernetes missing

    # Limitations must be explicitly stated
    assert len(match_dto.limitations) > 0

    # Retrieve match by ID
    fetched = get_job_match(match_id=match_dto.id, current_user=user, db=db_session)
    assert fetched.id == match_dto.id

