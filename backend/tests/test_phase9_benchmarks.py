import time
import pytest
from app.models.assessment import Question, AssessmentAttempt
from app.services.sandbox import sandbox
from app.services.adaptive_engine import adaptive_engine
from app.services.question_bank_service import question_bank_service


def test_question_bank_search_latency(db_session):
    # Search response time must be under 150ms for paginated requests
    t0 = time.perf_counter()
    questions = question_bank_service.list_questions(
        db=db_session,
        category="dsa",
        difficulty="medium",
        limit=20,
    )
    duration_ms = (time.perf_counter() - t0) * 1000.0
    assert duration_ms < 150.0  # Fast indexed retrieval


def test_sandbox_execution_latency():
    code = """
def max_subarray(nums):
    max_sum = current_sum = nums[0]
    for x in nums[1:]:
        current_sum = max(x, current_sum + x)
        max_sum = max(max_sum, current_sum)
    return max_sum
"""
    test_cases = [
        {"inputs": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
        {"inputs": [[1]], "expected": 1},
        {"inputs": [[5, 4, -1, 7, 8]], "expected": 23},
    ]

    t0 = time.perf_counter()
    result = sandbox.run_tests(code, "max_subarray", test_cases)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    assert result["status"] == "passed"
    assert result["passed_tests"] == 3
    # Subprocess execution, AST complexity check and test validation must finish under 1500ms
    assert duration_ms < 1500.0


def test_adaptive_mastery_calculation_performance():
    attempts = [
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="very_easy", difficulty_level=1, prompt="p1", question_type="mcq", evaluation_metadata={}),
        ),
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="easy", difficulty_level=2, prompt="p2", question_type="mcq", evaluation_metadata={}),
        ),
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="medium", difficulty_level=3, prompt="p3", question_type="mcq", evaluation_metadata={}),
        ),
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="hard", difficulty_level=4, prompt="p4", question_type="coding", evaluation_metadata={}),
        ),
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="very_hard", difficulty_level=5, prompt="p5", question_type="coding", evaluation_metadata={}),
        ),
        AssessmentAttempt(
            score=100.0,
            is_correct=True,
            question=Question(difficulty="expert", difficulty_level=6, prompt="p6", question_type="coding", evaluation_metadata={}),
        ),
    ]

    t0 = time.perf_counter()
    mastery = adaptive_engine.calculate_calibrated_mastery_score(attempts)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    assert duration_ms < 20.0  # Must be sub-millisecond to under 20ms
    assert mastery["mastery_score"] >= 9.5
    assert mastery["mastery_band"] == "Master / Principal"
