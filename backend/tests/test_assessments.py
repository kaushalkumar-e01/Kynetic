from app.models.user import User
from app.models.assessment import Question
from app.models.skill import EvidenceRecord, UserCapability
from app.core.security import get_password_hash
from app.schemas.assessment import CreateAssessmentRequest, SubmitAnswerRequest, SubmitCodeRequest
from app.services.assessment_service import assessment_service
from app.api.v1.endpoints.assessments import (
    list_topics,
    list_questions,
    create_assessment,
    get_assessment,
    submit_answer,
    submit_code,
    get_assessment_results,
)


def test_seed_and_list_topics(db_session):
    topics = list_topics(db=db_session)
    assert len(topics) >= 3
    topic_names = [t.name for t in topics]
    assert "Python Programming" in topic_names
    assert "Data Structures & Algorithms" in topic_names
    assert "SQL & Relational Databases" in topic_names


def test_public_questions_do_not_leak_answers(db_session):
    questions = list_questions(limit=10, db=db_session)
    assert len(questions) > 0
    for q in questions:
        # Pydantic schema QuestionPublicResponse must not have evaluation_metadata
        assert not hasattr(q, "evaluation_metadata")
        assert not hasattr(q, "correct_answer")


def test_assessment_flow_adaptive_progression(db_session):
    user = User(email="adaptive_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Start assessment
    req = CreateAssessmentRequest(
        title="Python Mastery Test",
        mode="assessment",
        selected_topics=["Python Programming"],
    )
    assessment_res = create_assessment(payload=req, current_user=user, db=db_session)
    assert assessment_res.title == "Python Mastery Test"
    assert assessment_res.status == "in_progress"
    assert assessment_res.current_question is not None
    assert assessment_res.current_question.difficulty == "easy"

    q1_id = assessment_res.current_question.id

    # 2. Submit correct answer for Q1
    ans_req = SubmitAnswerRequest(question_id=q1_id, answer="False")
    attempt1 = submit_answer(assessment_id=assessment_res.id, payload=ans_req, current_user=user, db=db_session)
    assert attempt1.is_correct is True
    assert attempt1.score == 100.0

    # 3. Fetch next question
    assessment_state = get_assessment(assessment_id=assessment_res.id, current_user=user, db=db_session)
    q2 = assessment_state.current_question
    assert q2 is not None
    assert q2.id != q1_id

    # 4. Check that demonstrated assessment evidence was recorded in capabilities
    evidence = db_session.query(EvidenceRecord).filter_by(user_id=user.id, source_type="assessment").first()
    assert evidence is not None
    assert evidence.confidence == 0.85

    capability = db_session.query(UserCapability).filter_by(user_id=user.id).first()
    assert capability is not None
    assert capability.estimated_band == "foundational"
    assert capability.score == 10.0


def test_coding_assessment_submission(db_session):
    user = User(email="coder@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assessment_service.seed_initial_bank_if_empty(db_session)

    # Find the reverse_string coding question
    coding_q = (
        db_session.query(Question)
        .filter(Question.question_type == "coding", Question.prompt.ilike("%reverse_string%"))
        .first()
    )
    assert coding_q is not None

    req = CreateAssessmentRequest(
        title="Coding Challenge",
        mode="assessment",
        selected_topics=["Python Programming"],
    )
    assessment_res = create_assessment(payload=req, current_user=user, db=db_session)

    # Submit valid solution
    valid_code = "def reverse_string(s: str) -> str:\n    return s[::-1]\n"
    code_req = SubmitCodeRequest(question_id=coding_q.id, code=valid_code)
    attempt = submit_code(assessment_id=assessment_res.id, payload=code_req, current_user=user, db=db_session)

    assert attempt.is_correct is True
    assert attempt.score == 100.0
    assert attempt.execution_result["status"] == "passed"

    # Finish and check summary results
    results = get_assessment_results(assessment_id=assessment_res.id, current_user=user, db=db_session)
    assert results.status == "completed"
    assert results.average_score == 100.0
    assert results.total_questions == 1

