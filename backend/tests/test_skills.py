from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.skill import CreateEvidenceRequest
from app.api.v1.endpoints.skills import list_skills, list_user_capabilities, add_user_evidence


def test_skills_and_capabilities_workflow(db_session):
    user = User(email="skills_api_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Add user-confirmed evidence
    payload = CreateEvidenceRequest(
        skill_name="Docker",
        category="devops",
        summary="Built multi-stage Docker container images for microservices.",
        confidence=0.8,
    )
    evidence_res = add_user_evidence(payload=payload, current_user=user, db=db_session)
    assert evidence_res.source_type == "user-confirmed"
    assert evidence_res.confidence == 0.8

    # 2. Check capabilities endpoint
    capabilities = list_user_capabilities(current_user=user, db=db_session)
    assert len(capabilities) == 1
    assert capabilities[0].skill_name == "Docker"
    assert capabilities[0].estimated_band == "claimed"
    assert capabilities[0].confidence > 0.0

    # 3. Check skills catalog
    skills = list_skills(db=db_session)
    assert any(s.canonical_name == "Docker" for s in skills)

