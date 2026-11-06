import re
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException, BadRequestException
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
    QuestionBankStatsResponse,
    AIGenerateBatchRequest,
    AIGenerateBatchResponse,
)
from app.services.assessment_service import assessment_service
from app.services.adaptive_engine import adaptive_engine
from app.services.question_bank_builder import question_bank_builder
from app.services.question_bank_service import question_bank_service

router = APIRouter()


def serialize_public_question(q: Question) -> QuestionPublicResponse:
    meta = q.evaluation_metadata or {}
    sample_tc = meta.get("sample_test_cases")
    if not sample_tc and meta.get("test_cases"):
        sample_tc = meta.get("test_cases")[:3]

    entry = meta.get("entry_point", "solution")
    raw_starter_codes = meta.get("starter_codes") or {}
    starter_codes: Dict[str, str] = {}
    if q.question_type == "coding":
        default_starters = {
            "python": f"def {entry}(*args):\n    # Write your solution here\n    pass\n",
            "javascript": f"function {entry}(...args) {{\n    // Write your solution here\n}}\n",
            "typescript": f"function {entry}(...args): any {{\n    // Write your solution here\n}}\n",
            "c": f"// Implement {entry}\nint {entry}() {{\n    return 0;\n}}\n",
            "cpp": f"class Solution {{\npublic:\n    int {entry}() {{\n        return 0;\n    }}\n}};\n",
            "java": f"class Solution {{\n    public int {entry}() {{\n        return 0;\n    }}\n}}\n",
        }
        for lang_key in ("python", "javascript", "typescript", "c", "cpp", "java"):
            starter_codes[lang_key] = raw_starter_codes.get(lang_key) or default_starters[lang_key]

    starter = meta.get("starter_code")
    if not starter and q.question_type == "coding":
        lang = (q.programming_language or "python").lower()
        starter = starter_codes.get(lang, starter_codes.get("python"))
    elif not starter and q.question_type == "output_prediction":
        starter = meta.get("code")
    elif not starter and q.question_type == "debugging":
        starter = meta.get("buggy_code")

    # Structured examples extraction
    examples = meta.get("examples")
    if not examples and sample_tc:
        examples = []
        for tc in sample_tc:
            inp_str = str(tc.get("inputs")) if tc.get("inputs") is not None else ""
            out_str = str(tc.get("expected")) if tc.get("expected") is not None else ""
            examples.append({"input": inp_str, "output": out_str})

    constraints = meta.get("constraints") or meta.get("key_concepts") or []

    raw_title = q.title or meta.get("title") or ""
    clean_title = re.sub(r"^###\s*", "", raw_title).strip()
    clean_prompt = q.prompt or ""
    if not clean_title and clean_prompt.startswith("### "):
        m = re.match(r"^###\s*([^\n]+)", clean_prompt)
        if m:
            clean_title = m.group(1).strip()

    if clean_title and clean_prompt.startswith("### "):
        clean_prompt = re.sub(r"^###\s*[^\n]+\n*", "", clean_prompt).strip()

    return QuestionPublicResponse(
        id=q.id,
        topic_id=q.topic_id,
        category=q.category or "cs_fundamentals",
        subtopic=q.subtopic,
        question_type=q.question_type,
        difficulty=q.difficulty,
        difficulty_level=q.difficulty_level,
        programming_language=q.programming_language,
        title=clean_title or "Technical Assessment Challenge",
        prompt=clean_prompt,
        options=q.options or [],
        starter_code=starter,
        starter_codes=starter_codes if starter_codes else None,
        examples=examples if examples else None,
        constraints=constraints,
        sample_test_cases=sample_tc or [],
        schema_ddl=meta.get("schema_ddl"),
        source_attribution=q.source_attribution,
        validation_status=q.validation_status or "validated",
    )


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
    return [serialize_public_question(q) for q in questions]


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
    if not next_q:
        db.delete(assessment)
        db.commit()
        topics_str = ", ".join(payload.selected_topics) if payload.selected_topics else "selected topics"
        raise BadRequestException(
            f"No questions currently available matching {topics_str} in '{payload.mode}' mode. Please choose another domain or mode."
        )

    dto = AssessmentResponse.model_validate(assessment)
    dto.current_question = serialize_public_question(next_q)
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
        dto.current_question = serialize_public_question(next_q)
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
    if assessment.status != "in_progress":
        raise BadRequestException(f"Cannot submit answer to assessment with status '{assessment.status}'.")

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
    "/assessments/{assessment_id}/run-code",
    summary="Run code against sample test cases in sandbox without submitting",
)
def run_code_test(
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
    if assessment.status != "in_progress":
        raise BadRequestException(f"Cannot submit answer to assessment with status '{assessment.status}'.")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise NotFoundException("Question not found.")

    return assessment_service.run_code_test(question=question, code_str=payload.code)


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
    if assessment.status != "in_progress":
        raise BadRequestException(f"Cannot submit answer to assessment with status '{assessment.status}'.")

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

    mastery_eval = adaptive_engine.calculate_calibrated_mastery_score(attempts)

    if assessment.status != "completed":
        assessment.status = "completed"
        assessment.completed_at = datetime.now(timezone.utc)
        assessment.summary_result = {
            "total_questions": total_q,
            "correct_answers": correct_count,
            "average_score": round(avg_score, 1),
            "mastery_score": mastery_eval["mastery_score"],
            "mastery_band": mastery_eval["mastery_band"],
            "highest_tier_passed": mastery_eval["highest_tier_passed"],
            "highest_tier_level": mastery_eval["highest_tier_level"],
            "ceiling_applied": mastery_eval["ceiling_applied"],
            "estimated_ability": mastery_eval["estimated_ability"],
            "subtopic_abilities": mastery_eval["subtopic_abilities"],
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
        mastery_score=mastery_eval["mastery_score"],
        mastery_band=mastery_eval["mastery_band"],
        highest_tier_passed=mastery_eval["highest_tier_passed"],
        estimated_ability=mastery_eval["estimated_ability"],
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


@router.get(
    "/question-bank/stats",
    response_model=QuestionBankStatsResponse,
    summary="Get comprehensive question bank statistics and distribution",
)
def get_question_bank_statistics(db: Session = Depends(get_db)):
    return QuestionBankStatsResponse(**question_bank_builder.get_bank_statistics(db))


@router.get(
    "/question-bank/questions",
    response_model=List[QuestionPublicResponse],
    summary="Search and filter the question bank with pagination",
)
def search_question_bank(
    category: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    question_type: Optional[str] = None,
    programming_language: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    questions = question_bank_service.list_questions(
        db=db,
        category=category,
        topic_name=topic,
        difficulty=difficulty,
        difficulty_level=difficulty_level,
        question_type=question_type,
        programming_language=programming_language,
        search_query=search,
        skip=skip,
        limit=min(100, limit),
    )
    return [QuestionPublicResponse.model_validate(q) for q in questions]


@router.post(
    "/question-bank/generate-batch",
    response_model=AIGenerateBatchResponse,
    summary="Trigger automatic AI generation and validation of technical questions",
)
def generate_ai_questions_batch(
    payload: AIGenerateBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = question_bank_service.generate_ai_question_batch(
        skill_or_topic=payload.skill_or_topic,
        category=payload.category,
        difficulty=payload.difficulty,
        question_type=payload.question_type,
        batch_size=payload.batch_size,
        db=db,
        programming_language=payload.programming_language,
    )
    return AIGenerateBatchResponse(**result)


@router.post(
    "/question-bank/questions/{question_id}/validate",
    summary="Run validation on a question and update its lifecycle status",
)
def validate_question_endpoint(
    question_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_valid, msg, question = question_bank_service.validate_question_by_id(question_id, db)
    if not question:
        raise NotFoundException("Question not found.")
    return {
        "question_id": question.id,
        "is_valid": is_valid,
        "validation_status": question.validation_status,
        "audit_message": msg,
    }

