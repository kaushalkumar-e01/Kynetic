from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.assessment import AssessmentTopic, Question, Assessment, AssessmentAttempt
from app.models.activity import UserActivity
from app.schemas.assessment import (
    AssessmentTopicResponse,
    QuestionPublicResponse,
    CreateAssessmentRequest,
    SubmitAnswerRequest,
    SubmitCodeRequest,
    AssessmentAttemptResponse,
    AssessmentResponse,
    AssessmentSummaryResultsResponse,
)
from app.services.assessment_service import assessment_service

router = APIRouter()


@router.get(
    "/assessment-topics",
    response_model=List[AssessmentTopicResponse],
    summary="List available assessment topics",
)
def list_topics(db: Session = Depends(get_db)):
    assessment_service.seed_initial_bank_if_empty(db)
    topics = db.query(AssessmentTopic).order_by(AssessmentTopic.name).all()
    return [AssessmentTopicResponse.model_validate(t) for t in topics]


@router.get(
    "/questions",
    response_model=List[QuestionPublicResponse],
    summary="List active questions (without hidden answers)",
)
def list_questions(
    topic_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    assessment_service.seed_initial_bank_if_empty(db)
    query = db.query(Question).filter(Question.is_active.is_(True))
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty.lower())

    actual_limit = limit if isinstance(limit, int) else 50
    questions = query.limit(actual_limit).all()
    return [QuestionPublicResponse.model_validate(q) for q in questions]


@router.post(
    "/assessments",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new skill assessment or practice session",
)
def create_assessment(
    payload: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment_service.seed_initial_bank_if_empty(db)

    title = payload.title or f"{payload.mode.title()} Assessment ({datetime.now().strftime('%b %d')})"
    assessment = Assessment(
        user_id=current_user.id,
        title=title,
        mode=payload.mode,
        selected_topics=payload.selected_topics,
        status="in_progress",
    )
    db.add(assessment)
    db.flush()

    activity = UserActivity(
        user_id=current_user.id,
        activity_type="assessment_started",
        related_record_type="assessment",
        related_record_id=assessment.id,
        details={"mode": payload.mode, "topics": payload.selected_topics},
    )
    db.add(activity)
    db.commit()
    db.refresh(assessment)

    # Get initial adaptive question
    next_q = assessment_service.get_next_question(assessment, db)
    dto = AssessmentResponse.model_validate(assessment)
    if next_q:
        dto.current_question = QuestionPublicResponse.model_validate(next_q)
    return dto


@router.get(
    "/assessments",
    response_model=List[AssessmentResponse],
    summary="List authenticated user's assessments",
)
def list_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(desc(Assessment.started_at))
        .all()
    )
    return [AssessmentResponse.model_validate(a) for a in assessments]


@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get assessment details and next question",
)
def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
        .first()
    )
    if not assessment:
        raise NotFoundException("Assessment not found or access denied.")

    next_q = assessment_service.get_next_question(assessment, db)
    dto = AssessmentResponse.model_validate(assessment)
    if next_q:
        dto.current_question = QuestionPublicResponse.model_validate(next_q)
    return dto


@router.post(
    "/assessments/{assessment_id}/answers",
    response_model=AssessmentAttemptResponse,
    summary="Submit answer for a multiple choice or conceptual question",
)
def submit_answer(
    assessment_id: str,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
        .first()
    )
    if not assessment:
        raise NotFoundException("Assessment not found or access denied.")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise NotFoundException("Question not found.")

    attempt = assessment_service.evaluate_quiz_answer(
        assessment=assessment,
        question=question,
        user_answer=payload.answer,
        user_id=current_user.id,
        db=db,
    )
    return AssessmentAttemptResponse.model_validate(attempt)


@router.post(
    "/assessments/{assessment_id}/code-submissions",
    response_model=AssessmentAttemptResponse,
    summary="Submit code for isolated sandbox execution",
)
def submit_code(
    assessment_id: str,
    payload: SubmitCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
        .first()
    )
    if not assessment:
        raise NotFoundException("Assessment not found or access denied.")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise NotFoundException("Question not found.")

    attempt = assessment_service.evaluate_code_submission(
        assessment=assessment,
        question=question,
        code_str=payload.code,
        user_id=current_user.id,
        db=db,
    )
    return AssessmentAttemptResponse.model_validate(attempt)


@router.get(
    "/assessments/{assessment_id}/results",
    response_model=AssessmentSummaryResultsResponse,
    summary="Get assessment performance summary and topic breakdown",
)
def get_assessment_results(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
        .first()
    )
    if not assessment:
        raise NotFoundException("Assessment not found or access denied.")

    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.assessment_id == assessment.id)
        .order_by(AssessmentAttempt.created_at)
        .all()
    )
    total_q = len(attempts)
    correct_count = sum(1 for a in attempts if a.is_correct is True)
    avg_score = (sum(a.score for a in attempts) / total_q) if total_q > 0 else 0.0

    if assessment.status != "completed":
        assessment.status = "completed"
        assessment.completed_at = datetime.now(timezone.utc)
        assessment.summary_result = {
            "total_questions": total_q,
            "correct_answers": correct_count,
            "average_score": round(avg_score, 1),
        }
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="assessment_completed",
            related_record_type="assessment",
            related_record_id=assessment.id,
            details=assessment.summary_result,
        )
        db.add(activity)
        db.commit()

    return AssessmentSummaryResultsResponse(
        id=assessment.id,
        title=assessment.title,
        mode=assessment.mode,
        status=assessment.status,
        total_questions=total_q,
        correct_answers=correct_count,
        average_score=round(avg_score, 1),
        completed_at=assessment.completed_at,
        attempts=[AssessmentAttemptResponse.model_validate(a) for a in attempts],
    )


@router.get(
    "/assessment-attempts",
    response_model=List[AssessmentAttemptResponse],
    summary="List user's assessment attempt history",
)
def list_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.user_id == current_user.id)
        .order_by(desc(AssessmentAttempt.created_at))
        .all()
    )
    return [AssessmentAttemptResponse.model_validate(a) for a in attempts]

