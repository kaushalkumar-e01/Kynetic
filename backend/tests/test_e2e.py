import io
from fastapi import Response, UploadFile
from pypdf import PdfWriter

from app.models.user import User
from app.schemas.auth import UserRegisterRequest
from app.schemas.profile import UserProfileUpdate
from app.schemas.assessment import CreateAssessmentRequest, SubmitAnswerRequest
from app.schemas.project import ProjectCreate
from app.schemas.goal import JobMatchCreate
from app.schemas.roadmap import RoadmapCreate, MilestoneUpdate
from app.schemas.assistant import SendMessageRequest
from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.profile import update_user_profile
from app.api.v1.endpoints.resumes import upload_resume
from app.services.resume_service import resume_service
from app.api.v1.endpoints.assessments import (
    create_assessment,
    submit_answer,
)
from app.services.assessment_service import assessment_service
from app.api.v1.endpoints.projects import create_project, analyze_project_endpoint
from app.api.v1.endpoints.placement import create_job_match
from app.api.v1.endpoints.roadmaps import create_roadmap, update_milestone, get_roadmap
from app.api.v1.endpoints.assistant import send_assistant_message
from app.api.v1.endpoints.workspace import get_workspace_summary


def _create_test_pdf_bytes():
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    s = io.BytesIO()
    writer.write(s)
    return s.getvalue()


def test_full_kynetic_platform_e2e_flow(db_session, monkeypatch):
    # -------------------------------------------------------------
    # 1. User Registration & Authentication
    # -------------------------------------------------------------
    reg_req = UserRegisterRequest(
        email="kynetic_e2e@example.com",
        password="SecurePassword2026!",
        display_name="Kynetic Pioneer",
    )
    auth_res = register_user(payload=reg_req, response=Response(), db=db_session)
    user_id = auth_res.user.id
    user = db_session.query(User).filter_by(id=user_id).first()
    assert user is not None

    # -------------------------------------------------------------
    # 2. Profile Setup
    # -------------------------------------------------------------
    profile_req = UserProfileUpdate(
        headline="Full Stack & AI Engineer",
        preferred_domains=["Backend", "AI Systems"],
        learning_preferences={"daily_target_minutes": 45},
    )
    profile_dto = update_user_profile(payload=profile_req, current_user=user, db=db_session)
    assert profile_dto.headline == "Full Stack & AI Engineer"

    # -------------------------------------------------------------
    # 3. Resume Upload & AI Analysis (Claimed Evidence)
    # -------------------------------------------------------------
    resume_text = """
    Kynetic Pioneer
    Education: B.Tech Computer Science
    Projects: Distributed Web API in Python and FastAPI
    Skills: Python, FastAPI, SQL, Docker, React
    """
    monkeypatch.setattr("app.services.resume_service.extract_text_from_pdf", lambda path: resume_text)

    pdf_bytes = _create_test_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        size=len(pdf_bytes),
        filename="pioneer_resume.pdf",
        headers={"content-type": "application/pdf"},
    )
    resume_dto = upload_resume(file=upload, current_user=user, db=db_session)
    analysis = resume_service.analyze_resume_for_user(resume_id=resume_dto.id, user_id=user.id, db=db_session)
    assert analysis.status == "completed"

    # -------------------------------------------------------------
    # 4. Adaptive Assessment & Coding Submission (Demonstrated Evidence)
    # -------------------------------------------------------------
    assessment_service.seed_initial_bank_if_empty(db_session)

    # Start assessment in Python
    create_ass_req = CreateAssessmentRequest(
        title="Python Qualification Test",
        mode="assessment",
        selected_topics=["Python Programming"],
    )
    ass_dto = create_assessment(payload=create_ass_req, current_user=user, db=db_session)
    assert ass_dto.current_question is not None

    # Answer MCQ correctly
    q1_id = ass_dto.current_question.id
    ans_req = SubmitAnswerRequest(question_id=q1_id, answer="False")
    att1 = submit_answer(assessment_id=ass_dto.id, payload=ans_req, current_user=user, db=db_session)
    assert att1.score == 100.0

    # -------------------------------------------------------------
    # 5. Project Creation & Analysis (Practical Evidence)
    # -------------------------------------------------------------
    proj_req = ProjectCreate(
        name="Scalable Microservices Gateway",
        description="RESTful API service built with FastAPI, PostgreSQL, and Docker containerization.",
        source_type="github",
        repository_url="https://github.com/developer/gateway-service",
    )
    proj_dto = create_project(payload=proj_req, current_user=user, db=db_session)
    proj_analysis = analyze_project_endpoint(project_id=proj_dto.id, current_user=user, db=db_session)
    assert proj_analysis.status == "completed"
    assert "Fastapi" in proj_analysis.detected_technologies or "FastAPI" in proj_analysis.detected_technologies

    # -------------------------------------------------------------
    # 6. Placement Matching Against Job Description
    # -------------------------------------------------------------
    job_desc = """
    Senior Python Backend Engineer.
    Must have experience with Python, FastAPI, and SQL. Docker is preferred.
    """
    match_req = JobMatchCreate(
        role_title="Senior Python Backend Engineer",
        job_description=job_desc,
    )
    match_dto = create_job_match(payload=match_req, current_user=user, db=db_session)
    assert match_dto.estimated_score >= 60.0
    assert match_dto.match_breakdown["matched_count"] >= 1

    # -------------------------------------------------------------
    # 7. Personalized Learning Roadmap Generation
    # -------------------------------------------------------------
    roadmap_req = RoadmapCreate(
        title="Placement Preparation Roadmap",
        target_skills=["Python", "FastAPI", "Docker"],
    )
    roadmap_dto = create_roadmap(payload=roadmap_req, current_user=user, db=db_session)
    assert len(roadmap_dto.milestones) == 4

    # Complete Milestone 1
    m1_id = roadmap_dto.milestones[0].id
    update_milestone(
        roadmap_id=roadmap_dto.id,
        milestone_id=m1_id,
        payload=MilestoneUpdate(status="completed"),
        current_user=user,
        db=db_session,
    )
    updated_roadmap = get_roadmap(roadmap_id=roadmap_dto.id, current_user=user, db=db_session)
    assert updated_roadmap.progress_percentage == 25.0

    # -------------------------------------------------------------
    # 8. AI Assistant Chat with Workspace Context
    # -------------------------------------------------------------
    chat_req = SendMessageRequest(message="What are my top capabilities and what should I learn next?")
    conv_dto = send_assistant_message(payload=chat_req, current_user=user, db=db_session)
    assert len(conv_dto.messages) == 2
    # Verify assistant references user's tracked skills
    assert "Python" in conv_dto.messages[1].content

    # -------------------------------------------------------------
    # 9. Workspace Summary Aggregation
    # -------------------------------------------------------------
    summary = get_workspace_summary(current_user=user, db=db_session)
    assert summary.user.email == "kynetic_e2e@example.com"
    assert summary.resumes_count == 1
    assert summary.projects_count == 1
    assert summary.assessments_count == 1
    assert summary.roadmaps_count == 1
    assert summary.active_roadmap is not None
    assert len(summary.recent_activities) >= 5
