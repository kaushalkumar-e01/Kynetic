from app.models.user import User
from app.models.skill import EvidenceRecord, UserCapability
from app.core.security import get_password_hash
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.api.v1.endpoints.projects import (
    create_project,
    list_projects,
    get_project,
    update_project,
    analyze_project_endpoint,
)


def test_project_crud_lifecycle(db_session):
    user = User(email="proj_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Create project
    create_req = ProjectCreate(
        name="Distributed Event Streaming Platform",
        description="Event stream processing using FastAPI, Redis, and PostgreSQL",
        source_type="manual",
    )
    project_dto = create_project(payload=create_req, current_user=user, db=db_session)
    assert project_dto.name == "Distributed Event Streaming Platform"
    assert project_dto.source_type == "manual"

    # 2. List projects
    projects = list_projects(current_user=user, db=db_session)
    assert len(projects) == 1
    assert projects[0].id == project_dto.id

    # 3. Update project
    update_req = ProjectUpdate(description="Updated description with Docker and Kubernetes")
    updated_dto = update_project(project_id=project_dto.id, payload=update_req, current_user=user, db=db_session)
    assert "Docker" in updated_dto.description

    # 4. Get project
    fetched = get_project(project_id=project_dto.id, current_user=user, db=db_session)
    assert fetched.id == project_dto.id


def test_project_analysis_and_evidence_generation(db_session):
    user = User(email="proj_analyzer@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    create_req = ProjectCreate(
        name="Microservices Architecture with FastAPI and PostgreSQL",
        description="Scalable REST API service containerized with Docker, using SQLAlchemy and Pytest.",
        source_type="github",
        repository_url="https://github.com/developer/microservices-app",
    )
    project_dto = create_project(payload=create_req, current_user=user, db=db_session)

    # Trigger analysis
    analysis_dto = analyze_project_endpoint(project_id=project_dto.id, current_user=user, db=db_session)

    assert analysis_dto.status == "completed"
    assert len(analysis_dto.detected_technologies) >= 3
    assert "Fastapi" in analysis_dto.detected_technologies or "FastAPI" in analysis_dto.detected_technologies
    assert len(analysis_dto.missing_requirements) > 0
    assert len(analysis_dto.recommendations) > 0

    # Verify project evidence was ingested
    evidence = db_session.query(EvidenceRecord).filter_by(user_id=user.id, source_type="project").all()
    assert len(evidence) >= 2
    assert all(e.confidence == 0.7 for e in evidence)

    # Verify user capability was updated
    cap = db_session.query(UserCapability).filter_by(user_id=user.id).first()
    assert cap is not None
    assert cap.score >= 65.0

