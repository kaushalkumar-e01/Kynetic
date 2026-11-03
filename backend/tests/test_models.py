from app.models.user import User, UserProfile
from app.models.resume import Resume, ResumeAnalysis
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.project import Project
from app.models.goal import Goal


def test_user_and_profile_creation(db_session):
    user = User(
        email="test@example.com",
        password_hash="hashed_pw_secret",
        account_status="active",
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert len(user.id) == 36
    assert user.created_at is not None

    profile = UserProfile(
        user_id=user.id,
        display_name="Ketan Dev",
        headline="Software Engineer",
        preferred_domains=["Backend", "AI"],
    )
    db_session.add(profile)
    db_session.flush()

    assert profile.user_id == user.id
    assert user.profile.display_name == "Ketan Dev"


def test_resume_and_analysis_relationship(db_session):
    user = User(email="resume_test@example.com", password_hash="secret")
    db_session.add(user)
    db_session.flush()

    resume = Resume(
        user_id=user.id,
        file_storage_key="resumes/test_resume.pdf",
        original_filename="resume.pdf",
        file_size=10240,
        status="uploaded",
    )
    db_session.add(resume)
    db_session.flush()

    analysis = ResumeAnalysis(
        user_id=user.id,
        resume_id=resume.id,
        status="completed",
        strengths=["Python", "FastAPI"],
    )
    db_session.add(analysis)
    db_session.flush()

    assert len(resume.analyses) == 1
    assert resume.analyses[0].strengths == ["Python", "FastAPI"]


def test_skill_and_capability(db_session):
    user = User(email="skill_test@example.com", password_hash="secret")
    skill = Skill(canonical_name="Python", category="language", description="Python 3")
    db_session.add_all([user, skill])
    db_session.flush()

    capability = UserCapability(
        user_id=user.id,
        skill_id=skill.id,
        estimated_band="proficient",
        score=85.0,
        confidence=0.8,
        evidence_count=2,
    )
    evidence = EvidenceRecord(
        user_id=user.id,
        skill_id=skill.id,
        source_type="assessment",
        summary="Passed advanced Python quiz",
        confidence=0.9,
    )
    db_session.add_all([capability, evidence])
    db_session.flush()

    assert capability.score == 85.0
    assert len(skill.evidence_records) == 1
    assert user.user_capabilities[0].estimated_band == "proficient"


def test_cascade_delete_user(db_session):
    user = User(email="delete_test@example.com", password_hash="secret")
    db_session.add(user)
    db_session.flush()

    project = Project(
        user_id=user.id,
        name="Kynetic Backend",
        source_type="github",
        repository_url="https://github.com/example/kynetic",
    )
    goal = Goal(
        user_id=user.id,
        goal_type="placement",
        title="Backend Engineer at Tech Co",
    )
    db_session.add_all([project, goal])
    db_session.flush()

    assert len(user.projects) == 1
    assert len(user.goals) == 1

    # Delete user and verify cascading deletion
    db_session.delete(user)
    db_session.flush()

    remaining_projects = db_session.query(Project).filter_by(user_id=user.id).all()
    remaining_goals = db_session.query(Goal).filter_by(user_id=user.id).all()
    assert len(remaining_projects) == 0
    assert len(remaining_goals) == 0

