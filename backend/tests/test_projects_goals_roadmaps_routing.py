import pytest
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.project import ProjectCreate
from app.schemas.goal import GoalCreate
from app.schemas.roadmap import RoadmapCreate
from app.api.v1.endpoints.projects import list_projects, create_project
from app.api.v1.endpoints.goals import list_goals, create_goal
from app.api.v1.endpoints.roadmaps import list_roadmaps, create_roadmap


def test_projects_tab_independent_of_assessment(db_session):
    user = User(email="proj_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Listing projects without any assessments should return empty list without error
    projects = list_projects(current_user=user, db=db_session)
    assert projects == []

    # 2. Creating a project without any assessment should succeed
    payload = ProjectCreate(
        name="Distributed Cache Engine",
        description="High-throughput in-memory cache with LRU eviction",
        source_type="manual",
        technologies=["Python", "Redis"],
    )
    created = create_project(payload=payload, current_user=user, db=db_session)
    assert created.id is not None
    assert created.name == "Distributed Cache Engine"

    # 3. Listing again should include the project
    projects_after = list_projects(current_user=user, db=db_session)
    assert len(projects_after) == 1
    assert projects_after[0].id == created.id


def test_goals_tab_independent_of_assessment(db_session):
    user = User(email="goal_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Listing goals without any assessments should return empty list without error
    goals = list_goals(current_user=user, db=db_session)
    assert goals == []

    # 2. Creating a goal without any assessment should succeed
    payload = GoalCreate(
        title="Become a Principal Cloud Architect",
        goal_type="career",
        description="Master distributed systems, microservices, and Kubernetes orchestration",
    )
    created = create_goal(payload=payload, current_user=user, db=db_session)
    assert created.id is not None
    assert created.title == "Become a Principal Cloud Architect"

    # 3. Listing again should include the goal
    goals_after = list_goals(current_user=user, db=db_session)
    assert len(goals_after) == 1
    assert goals_after[0].id == created.id


def test_roadmaps_tab_independent_of_assessment(db_session):
    user = User(email="roadmap_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Listing roadmaps without any assessments should return empty list without error
    roadmaps = list_roadmaps(current_user=user, db=db_session)
    assert roadmaps == []

    # 2. Generating a roadmap without any assessment should succeed
    payload = RoadmapCreate(
        title="Backend Engineering Mastery",
        description="Comprehensive curriculum for backend engineering",
        target_skills=["Python", "FastAPI", "SQL"],
    )
    created = create_roadmap(payload=payload, current_user=user, db=db_session)
    assert created.id is not None
    assert created.title == "Backend Engineering Mastery"
    assert len(created.milestones) > 0

    # 3. Listing again should include the roadmap
    roadmaps_after = list_roadmaps(current_user=user, db=db_session)
    assert len(roadmaps_after) == 1
    assert roadmaps_after[0].id == created.id


def test_http_routes_do_not_route_projects_goals_roadmaps_to_assessment():
    from starlette.routing import Match
    from app.main import app

    test_cases = [
        ("/api/v1/projects", "list_projects"),
        ("/api/v1/goals", "list_goals"),
        ("/api/v1/roadmaps", "list_roadmaps"),
    ]

    for path, expected_func in test_cases:
        scope = {"type": "http", "method": "GET", "path": path}
        matched_endpoint = None
        for route in app.routes:
            match, _ = route.matches(scope)
            if match == Match.FULL:
                matched_endpoint = getattr(route.endpoint, "__name__", None)
                break
        assert matched_endpoint == expected_func, f"Expected {path} to resolve to {expected_func}, but got {matched_endpoint}"

