from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.roadmap import RoadmapCreate, MilestoneCreate, MilestoneUpdate
from app.api.v1.endpoints.roadmaps import (
    create_roadmap,
    get_roadmap,
    add_milestone,
    update_milestone,
)


def test_roadmap_generation_and_progress_tracking(db_session):
    user = User(email="roadmap_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Generate roadmap
    req = RoadmapCreate(
        title="Full Stack Capability Roadmap",
        description="Master FastAPI, React, and PostgreSQL for placement preparation",
        target_skills=["FastAPI", "React", "PostgreSQL"],
    )
    roadmap_dto = create_roadmap(payload=req, current_user=user, db=db_session)

    assert roadmap_dto.title == "Full Stack Capability Roadmap"
    assert roadmap_dto.status == "active"
    assert len(roadmap_dto.milestones) == 4  # 3 skills + 1 capstone project
    assert roadmap_dto.progress_percentage == 0.0

    m1_id = roadmap_dto.milestones[0].id

    # 2. Update Milestone 1 to completed
    ms_update = MilestoneUpdate(status="completed")
    updated_m1 = update_milestone(
        roadmap_id=roadmap_dto.id,
        milestone_id=m1_id,
        payload=ms_update,
        current_user=user,
        db=db_session,
    )
    assert updated_m1.status == "completed"

    # 3. Check updated roadmap progress
    fetched_roadmap = get_roadmap(roadmap_id=roadmap_dto.id, current_user=user, db=db_session)
    # 1 of 4 completed = 25%
    assert fetched_roadmap.progress_percentage == 25.0

    # 4. Add a custom milestone
    custom_ms_req = MilestoneCreate(
        title="Deploy to AWS Cloud",
        description="Set up ECS Fargate cluster and RDS database instance",
        ordering=5,
    )
    added_ms = add_milestone(roadmap_id=roadmap_dto.id, payload=custom_ms_req, current_user=user, db=db_session)
    assert added_ms.title == "Deploy to AWS Cloud"

    # Now 1 of 5 completed = 20%
    fetched_roadmap2 = get_roadmap(roadmap_id=roadmap_dto.id, current_user=user, db=db_session)
    assert fetched_roadmap2.progress_percentage == 20.0

