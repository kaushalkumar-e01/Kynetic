import pytest
from app.models.assessment import Assessment, Question, AssessmentTopic
from app.services.assessment_service import assessment_service
from app.services.sandbox import sandbox


def test_sandbox_python_execution():
    code = """
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        diff = target - x
        if diff in seen:
            return [seen[diff], i]
        seen[x] = i
    return []
"""
    test_cases = [
        {"inputs": [[2, 7, 11, 15], 9], "expected": [0, 1]},
        {"inputs": [[3, 2, 4], 6], "expected": [1, 2]},
    ]
    res = sandbox.run_tests(code, "two_sum", test_cases)
    assert res["status"] == "passed"
    assert res["passed_tests"] == 2
    assert res["total_tests"] == 2


def test_sandbox_security_rejections():
    malicious_code = """
import os
def hack():
    os.system('dir')
    return True
"""
    res = sandbox.run_tests(malicious_code, "hack", [{"inputs": [], "expected": True}])
    assert res["status"] == "forbidden"
    assert "prohibited" in res["error_message"].lower()


def test_sql_execution_in_isolated_db(db_session):
    assessment_service.seed_initial_bank_if_empty(db_session)
    topic = db_session.query(AssessmentTopic).first()

    sql_q = Question(
        topic_id=topic.id,
        category="sql",
        subtopic="Aggregation",
        question_type="sql",
        difficulty="easy",
        difficulty_level=2,
        prompt="Select department and count from staff",
        options=[],
        evaluation_metadata={
            "schema_ddl": "CREATE TABLE staff (id INT, dept TEXT); INSERT INTO staff VALUES (1, 'Eng'), (2, 'Eng'), (3, 'HR');",
            "reference_query": "SELECT dept, COUNT(*) FROM staff GROUP BY dept ORDER BY dept;",
        },
        validation_status="validated",
        is_active=True,
    )
    db_session.add(sql_q)
    db_session.flush()

    assessment = Assessment(
        user_id="test_user",
        title="SQL Test Assessment",
        mode="sql",
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.flush()

    # 1. Correct query
    user_query = "SELECT dept, COUNT(*) FROM staff GROUP BY dept ORDER BY dept;"
    attempt = assessment_service.evaluate_quiz_answer(
        assessment=assessment,
        question=sql_q,
        user_answer=user_query,
        user_id="test_user",
        db=db_session,
    )
    assert attempt.is_correct is True
    assert attempt.score == 100.0

    # 2. Incorrect query
    wrong_query = "SELECT dept FROM staff;"
    attempt_wrong = assessment_service.evaluate_quiz_answer(
        assessment=assessment,
        question=sql_q,
        user_answer=wrong_query,
        user_id="test_user",
        db=db_session,
    )
    assert attempt_wrong.is_correct is False
    assert attempt_wrong.score == 0.0


def test_output_prediction_and_debugging_eval(db_session):
    assessment_service.seed_initial_bank_if_empty(db_session)
    topic = db_session.query(AssessmentTopic).first()

    out_q = Question(
        topic_id=topic.id,
        category="programming_languages",
        question_type="output_prediction",
        difficulty="very_easy",
        prompt="What is output?",
        options=["4", "3"],
        evaluation_metadata={"expected_output": "4", "explanation": "Appended element."},
        validation_status="validated",
        is_active=True,
    )
    db_session.add(out_q)

    debug_q = Question(
        topic_id=topic.id,
        category="dsa",
        question_type="debugging",
        difficulty="medium",
        prompt="Fix index shift bug",
        options=["Iterate backwards or copy list", "Use del keyword"],
        evaluation_metadata={"correct_fix": "Iterate backwards or copy list", "explanation": "Prevents index shift."},
        validation_status="validated",
        is_active=True,
    )
    db_session.add(debug_q)

    assessment = Assessment(
        user_id="test_user",
        title="Prediction & Debug Test",
        mode="quiz",
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.flush()

    # Test output prediction
    att_out = assessment_service.evaluate_quiz_answer(assessment, out_q, "4", "test_user", db_session)
    assert att_out.is_correct is True

    # Test debugging
    att_dbg = assessment_service.evaluate_quiz_answer(assessment, debug_q, "Iterate backwards or copy list", "test_user", db_session)
    assert att_dbg.is_correct is True


def test_conceptual_rubric_evaluation(db_session):
    assessment_service.seed_initial_bank_if_empty(db_session)
    topic = db_session.query(AssessmentTopic).first()

    concept_q = Question(
        topic_id=topic.id,
        category="cs_fundamentals",
        question_type="conceptual",
        difficulty="hard",
        prompt="Explain CAP Theorem trade-offs in distributed datastores.",
        options=[],
        evaluation_metadata={
            "rubric": "Consistency, Availability, and Partition Tolerance under network split.",
            "key_concepts": ["consistency", "availability", "partition tolerance"],
        },
        validation_status="validated",
        is_active=True,
    )
    db_session.add(concept_q)

    assessment = Assessment(
        user_id="test_user",
        title="Conceptual Test",
        mode="mixed",
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.flush()

    # Complete answer covering key concepts
    good_answer = "Under a network partition, a distributed system must choose between consistency and availability."
    att = assessment_service.evaluate_quiz_answer(assessment, concept_q, good_answer, "test_user", db_session)
    assert att.is_correct is True
    assert att.score >= 50.0

