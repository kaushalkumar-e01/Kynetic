import pytest
from app.models.user import User
from app.models.skill import Skill, UserCapability, EvidenceRecord
from app.models.assessment import AssessmentTopic, Question
from app.core.security import get_password_hash
from app.services.capability_service import recalculate_user_capability, recalculate_all_capabilities_for_user
from app.services.assessment_service import assessment_service
from app.services.matching_service import matching_service
from app.services.roadmap_service import roadmap_service
from app.services.assistant_service import assistant_service


def test_calibrated_capability_ceilings(db_session):
    user = User(email="calibrated_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill_py = Skill(canonical_name="Python", category="language")
    db_session.add(skill_py)
    db_session.flush()

    # Case A: User passes 5 "very_easy" and "easy" questions (Level 1 & 2)
    # Raw points: easy_points capped at 20.0
    for i in range(5):
        ev = EvidenceRecord(
            user_id=user.id,
            skill_id=skill_py.id,
            source_type="assessment",
            source_record_id=f"q_easy_{i}",
            summary="Passed easy question",
            confidence=0.85,
            quality_metadata={"difficulty": "easy", "difficulty_level": 2, "is_correct": True, "score": 100.0},
        )
        db_session.add(ev)
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    assert cap.score <= 45.0
    assert cap.score == 20.0
    assert cap.estimated_band == "foundational"

    # Case B: User passes 3 Medium questions (Level 3)
    for i in range(3):
        ev = EvidenceRecord(
            user_id=user.id,
            skill_id=skill_py.id,
            source_type="assessment",
            source_record_id=f"q_med_{i}",
            summary="Passed medium question",
            confidence=0.85,
            quality_metadata={"difficulty": "medium", "difficulty_level": 3, "is_correct": True, "score": 100.0},
        )
        db_session.add(ev)
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    # Easy (20) + Medium (30) = 50.0. Level 3 ceiling is 65.0.
    assert cap.score == 50.0
    assert cap.estimated_band == "proficient"

    # Case C: User solves 2 Hard questions (Level 4)
    for i in range(2):
        ev = EvidenceRecord(
            user_id=user.id,
            skill_id=skill_py.id,
            source_type="assessment",
            source_record_id=f"q_hard_{i}",
            summary="Passed hard question",
            confidence=0.85,
            quality_metadata={"difficulty": "hard", "difficulty_level": 4, "is_correct": True, "score": 100.0},
        )
        db_session.add(ev)
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    # Easy (20) + Medium (30) + Hard (30 capped) = 75.0 (out of 75 max assessment points).
    assert cap.score == 75.0
    assert cap.estimated_band == "advanced"

    # Case D: User adds code-verified project (+15 pts) -> raw score 90.0, but capped at Level 4 ceiling (80.0)!
    ev_proj = EvidenceRecord(
        user_id=user.id,
        skill_id=skill_py.id,
        source_type="project",
        source_record_id="proj_1",
        summary="Verified FastAPI Backend",
        confidence=0.8,
        quality_metadata={"code_verified": True},
    )
    db_session.add(ev_proj)
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    # Strictly capped at 80.0 because highest passed assessment tier is Level 4!
    assert cap.score == 80.0
    assert cap.estimated_band == "advanced"

    # Case E: User passes Level 5 (very_hard) question -> ceiling lifts to 90.0
    ev_vh = EvidenceRecord(
        user_id=user.id,
        skill_id=skill_py.id,
        source_type="assessment",
        source_record_id="q_vh_1",
        summary="Passed very hard question",
        confidence=0.88,
        quality_metadata={"difficulty": "very_hard", "difficulty_level": 5, "is_correct": True, "score": 100.0},
    )
    db_session.add(ev_vh)
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    assert cap.score == 90.0
    assert cap.estimated_band == "expert"

    # Case F: User passes Level 6 (expert) challenge with multiple verified assessments and high confidence
    ev_exp1 = EvidenceRecord(
        user_id=user.id,
        skill_id=skill_py.id,
        source_type="assessment",
        source_record_id="q_exp_1",
        summary="Passed expert challenge",
        confidence=0.92,
        quality_metadata={"difficulty": "expert", "difficulty_level": 6, "is_correct": True, "score": 100.0},
    )
    ev_proj2 = EvidenceRecord(
        user_id=user.id,
        skill_id=skill_py.id,
        source_type="project",
        source_record_id="proj_2",
        summary="Verified Production Microservice",
        confidence=0.85,
        quality_metadata={"code_verified": True},
    )
    db_session.add_all([ev_exp1, ev_proj2])
    db_session.flush()

    cap = recalculate_user_capability(user.id, skill_py.id, db_session)
    # Level 6 passed, >= 4 questions passed, high confidence -> unlocks 95.0+!
    assert cap.score >= 95.0
    assert cap.estimated_band == "expert"


def test_dual_skill_demonstration_language_and_topic(db_session):
    user = User(email="dual_skill_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    topic = AssessmentTopic(name="Data Structures & Algorithms")
    db_session.add(topic)
    db_session.flush()

    # Coding question in Python under DSA topic
    q = Question(
        topic_id=topic.id,
        category="dsa",
        subtopic="Binary Trees",
        question_type="coding",
        difficulty="hard",
        difficulty_level=4,
        programming_language="python",
        prompt="Serialize and deserialize a binary tree.",
        options=[],
        evaluation_metadata={"entry_point": "serialize", "test_cases": [{"inputs": [1], "expected": 1}]},
    )
    db_session.add(q)
    db_session.flush()

    # Record assessment evidence
    assessment_service._record_assessment_evidence(user.id, q, is_correct=True, score=100.0, db=db_session)

    # Verify BOTH Data Structures and Python skills were created and updated
    caps = recalculate_all_capabilities_for_user(user.id, db_session)
    skill_names = [c.skill.canonical_name for c in caps if c.skill]
    assert "Data Structures" in skill_names or "Data Structures & Algorithms" in skill_names
    assert "Python" in skill_names

    py_cap = next(c for c in caps if c.skill and c.skill.canonical_name == "Python")
    assert py_cap.score > 0.0
    assert py_cap.evidence_count >= 1


def test_placement_match_integration_with_capabilities(db_session):
    user = User(email="placement_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill_py = Skill(canonical_name="Python", category="language")
    db_session.add(skill_py)
    db_session.flush()

    # Create capability with Level 5 expert rating
    cap = UserCapability(
        user_id=user.id,
        skill_id=skill_py.id,
        estimated_band="expert",
        score=92.0,
        confidence=0.88,
        evidence_count=5,
    )
    ev = EvidenceRecord(
        user_id=user.id,
        skill_id=skill_py.id,
        source_type="assessment",
        source_record_id="q1",
        summary="Passed expert assessment in Python",
        confidence=0.88,
    )
    db_session.add_all([cap, ev])
    db_session.commit()

    job_desc = "Requirements: Python backend engineering, building REST APIs with high throughput."
    match = matching_service.match_job_description(
        user_id=user.id,
        role_title="Senior Python Backend Engineer",
        job_description=job_desc,
        db=db_session,
    )

    assert match is not None
    assert match.estimated_score > 0.0
    matched_skills = [m for m in match.match_breakdown.get("matched_skills", []) if m["skill"].lower() == "python"]
    assert len(matched_skills) == 1
    assert matched_skills[0]["band"] == "expert"
    assert "Verified" in matched_skills[0]["provenance"]


def test_roadmap_milestone_adaptive_recommendation(db_session):
    user = User(email="roadmap_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill_py = Skill(canonical_name="Python", category="language")
    db_session.add(skill_py)
    db_session.flush()

    # User with baseline of 72.0% (Level 4 Hard)
    cap = UserCapability(
        user_id=user.id,
        skill_id=skill_py.id,
        estimated_band="advanced",
        score=72.0,
        confidence=0.75,
        evidence_count=3,
    )
    db_session.add(cap)
    db_session.commit()

    roadmap = roadmap_service.generate_roadmap(
        user_id=user.id,
        title="Backend Mastery with Python",
        target_skills=["Python"],
        db=db_session,
    )

    assert roadmap is not None
    assert len(roadmap.milestones) >= 1
    py_milestone = roadmap.milestones[0]
    resources = py_milestone.resources
    adaptive_recs = [r for r in resources if r.get("type") == "adaptive_recommendation"]
    assert len(adaptive_recs) == 1
    assert "Level 4–5" in adaptive_recs[0]["title"]


def test_assistant_workspace_context_enrichment(db_session):
    user = User(email="assistant_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill_py = Skill(canonical_name="Python", category="language")
    db_session.add(skill_py)
    db_session.flush()

    cap = UserCapability(
        user_id=user.id,
        skill_id=skill_py.id,
        estimated_band="expert",
        score=95.0,
        confidence=0.90,
        evidence_count=6,
    )
    db_session.add(cap)
    db_session.commit()

    ctx = assistant_service.get_user_workspace_context(user.id, db_session)
    assert len(ctx["top_skills"]) == 1
    py_info = ctx["top_skills"][0]
    assert py_info["skill"] == "Python"
    assert py_info["score"] == 95.0
    assert py_info["mastery_score"] == 9.5
    assert py_info["band"] == "expert"
