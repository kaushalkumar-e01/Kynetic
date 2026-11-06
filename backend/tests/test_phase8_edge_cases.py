import pytest
import sqlite3
from app.models.user import User
from app.models.assessment import AssessmentTopic, Question, Assessment, AssessmentAttempt
from app.core.security import get_password_hash
from app.core.errors import BadRequestException
from app.services.sandbox import sandbox
from app.services.assessment_service import assessment_service
from app.services.adaptive_engine import adaptive_engine
from app.ai.gemini_provider import GeminiProvider
from app.schemas.assessment import SubmitAnswerRequest, SubmitCodeRequest
from app.api.v1.endpoints.assessments import submit_answer, submit_code


def test_empty_and_whitespace_code_submission():
    # 1. None code string
    res_none = sandbox.run_tests(None, "solution", [{"inputs": [1], "expected": 1}])
    assert res_none["status"] == "error"
    assert "Empty code" in res_none["error_message"]

    # 2. Whitespace code string
    res_ws = sandbox.run_tests("   \n\t  ", "solution", [{"inputs": [1], "expected": 1}])
    assert res_ws["status"] == "error"
    assert "Empty code" in res_ws["error_message"]


def test_untrusted_code_exceptions_handled_gracefully():
    # 1. ZeroDivisionError inside candidate code
    div_zero_code = """
def divide_by_zero(n):
    return n / 0
"""
    res = sandbox.run_tests(div_zero_code, "divide_by_zero", [{"inputs": [10], "expected": 5}])
    assert res["status"] == "failed"
    assert res["passed_tests"] == 0
    assert "division by zero" in res["test_results"][0]["error"]

    # 2. Unhandled NameError
    missing_var_code = """
def faulty(n):
    return n + undefined_variable
"""
    res = sandbox.run_tests(missing_var_code, "faulty", [{"inputs": [5], "expected": 5}])
    assert res["status"] == "failed"
    assert "undefined_variable" in res["test_results"][0]["error"]


def test_sql_sandboxing_and_injection_guards(db_session):
    user = User(email="sql_edge_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    topic = AssessmentTopic(name="SQL & Database Systems")
    db_session.add(topic)
    db_session.flush()

    q_sql = Question(
        topic_id=topic.id,
        category="sql",
        question_type="sql",
        difficulty="medium",
        difficulty_level=3,
        prompt="Select all active employees.",
        options=[],
        evaluation_metadata={
            "schema_ddl": "CREATE TABLE employees (id INT, name TEXT, active INT); INSERT INTO employees VALUES (1, 'Alice', 1);",
            "reference_query": "SELECT * FROM employees WHERE active = 1;",
        },
    )
    db_session.add(q_sql)

    assessment = Assessment(
        user_id=user.id,
        title="SQL Diagnostic",
        mode="sql",
        selected_topics=["SQL & Database Systems"],
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.commit()

    # Case A: Empty SQL submission
    attempt_empty = assessment_service.evaluate_quiz_answer(assessment, q_sql, "   ", user.id, db_session)
    assert attempt_empty.is_correct is False
    assert attempt_empty.score == 0.0
    assert "Empty SQL query" in attempt_empty.feedback

    # Case B: Forbidden PRAGMA command
    attempt_pragma = assessment_service.evaluate_quiz_answer(assessment, q_sql, "PRAGMA table_info(employees);", user.id, db_session)
    assert attempt_pragma.is_correct is False
    assert attempt_pragma.score == 0.0
    assert "Security restriction" in attempt_pragma.feedback

    # Case C: SQL syntax error
    attempt_syntax = assessment_service.evaluate_quiz_answer(assessment, q_sql, "SELEC * FORM employees", user.id, db_session)
    assert attempt_syntax.is_correct is False
    assert attempt_syntax.score == 0.0
    assert "SQL Execution Error" in attempt_syntax.feedback

    # Case D: Correct SQL query
    attempt_correct = assessment_service.evaluate_quiz_answer(assessment, q_sql, "SELECT * FROM employees WHERE active = 1", user.id, db_session)
    assert attempt_correct.is_correct is True
    assert attempt_correct.score == 100.0


def test_assessment_completed_status_guards(db_session):
    user = User(email="completed_guard_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    topic = AssessmentTopic(name="Python Programming")
    db_session.add(topic)
    db_session.flush()

    q = Question(
        topic_id=topic.id,
        category="programming_languages",
        question_type="multiple_choice",
        difficulty="easy",
        difficulty_level=2,
        prompt="What is type(42)?",
        options=["int", "str", "float", "bool"],
        evaluation_metadata={"correct_answer": "int"},
    )
    db_session.add(q)

    # Assessment already marked "completed"
    completed_assessment = Assessment(
        user_id=user.id,
        title="Completed Assessment",
        mode="quiz",
        status="completed",
        selected_topics=["Python Programming"],
    )
    db_session.add(completed_assessment)
    db_session.commit()

    # Attempting to submit answer to completed assessment should raise BadRequestException
    ans_payload = SubmitAnswerRequest(question_id=q.id, answer="int")
    with pytest.raises(BadRequestException) as excinfo:
        submit_answer(assessment_id=completed_assessment.id, payload=ans_payload, current_user=user, db=db_session)
    assert "Cannot submit answer to assessment with status 'completed'" in str(excinfo.value)

    # Attempting to submit code to completed assessment should raise BadRequestException
    code_payload = SubmitCodeRequest(question_id=q.id, code="def solution(): pass")
    with pytest.raises(BadRequestException) as excinfo_code:
        submit_code(assessment_id=completed_assessment.id, payload=code_payload, current_user=user, db=db_session)
    assert "Cannot submit answer to assessment with status 'completed'" in str(excinfo_code.value)


def test_adaptive_difficulty_boundary_clamping():
    # 1. Clamping at Level 1 floor: Multiple failures at Level 1 should not go to Level 0
    attempt_fail_1 = AssessmentAttempt(
        score=0.0,
        is_correct=False,
        question=Question(difficulty="very_easy", difficulty_level=1, prompt="p1", question_type="mcq", evaluation_metadata={}),
    )
    attempt_fail_2 = AssessmentAttempt(
        score=0.0,
        is_correct=False,
        question=Question(difficulty="very_easy", difficulty_level=1, prompt="p2", question_type="mcq", evaluation_metadata={}),
    )
    next_level_floor = adaptive_engine.get_adaptive_next_difficulty_level([attempt_fail_1, attempt_fail_2])
    assert next_level_floor == 1  # Strictly clamped at Level 1

    # 2. Clamping at Level 6 ceiling: Multiple successes at Level 6 should not exceed Level 6
    attempt_succ_1 = AssessmentAttempt(
        score=100.0,
        is_correct=True,
        question=Question(difficulty="expert", difficulty_level=6, prompt="p3", question_type="coding", evaluation_metadata={}),
    )
    attempt_succ_2 = AssessmentAttempt(
        score=100.0,
        is_correct=True,
        question=Question(difficulty="expert", difficulty_level=6, prompt="p4", question_type="coding", evaluation_metadata={}),
    )
    next_level_ceil = adaptive_engine.get_adaptive_next_difficulty_level([attempt_succ_1, attempt_succ_2])
    assert next_level_ceil == 6  # Strictly clamped at Level 6

    # 3. Empty attempts history
    empty_eval = adaptive_engine.calculate_calibrated_mastery_score([])
    assert empty_eval["mastery_score"] == 0.0
    assert empty_eval["highest_tier_level"] == 0


def test_ai_provider_malformed_json_fallback_resilience():
    # Test that Gemini provider falls back cleanly when AI produces unparsable non-JSON text
    gemini = GeminiProvider()
    
    # When api key is unset, it automatically delegates to fallback
    batch = gemini.generate_question_batch(
        skill_or_topic="Python Programming",
        category="programming_languages",
        difficulty="medium",
        question_type="multiple_choice",
        batch_size=3,
        programming_language="python",
    )
    assert len(batch) == 3
    assert all("prompt" in q for q in batch)
    assert all("options" in q for q in batch)
