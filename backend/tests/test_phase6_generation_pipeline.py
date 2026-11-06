import pytest
from app.models.assessment import Question, AssessmentTopic
from app.services.question_bank_service import question_bank_service, is_duplicate_prompt
from app.services.question_validator import question_validator


def test_lexical_jaccard_deduplication():
    existing = [
        "What is the average time complexity of searching for an element in a balanced Hash Table?",
        "Implement a function two_sum(nums, target) that returns indices of two numbers.",
    ]

    # 1. Nearly identical phrasing should be flagged as duplicate
    duplicate_candidate = "What is the average time complexity of searching an element in a balanced Hash Table?"
    assert is_duplicate_prompt(duplicate_candidate, existing, threshold=0.80) is True

    # 2. Distinct question should pass
    novel_candidate = "Explain the difference between optimistic and pessimistic concurrency control in distributed databases."
    assert is_duplicate_prompt(novel_candidate, existing, threshold=0.80) is False


def test_reference_solution_validation_gatekeeper():
    # 1. Valid Python coding challenge with correct reference solution
    valid_coding = {
        "prompt": "Write a function `add_numbers(a: int, b: int) -> int` returning their sum.",
        "question_type": "coding",
        "programming_language": "python",
        "evaluation_metadata": {
            "entry_point": "add_numbers",
            "test_cases": [
                {"inputs": [2, 3], "expected": 5},
                {"inputs": [-1, 1], "expected": 0},
            ],
            "reference_solution": "def add_numbers(a, b):\n    return a + b",
        },
    }
    is_valid, msg = question_validator.validate_question(valid_coding)
    assert is_valid is True
    assert "Valid" in msg

    # 2. Broken reference solution that fails its own test cases
    broken_coding = {
        "prompt": "Write a function `multiply(a: int, b: int) -> int` returning their product.",
        "question_type": "coding",
        "programming_language": "python",
        "evaluation_metadata": {
            "entry_point": "multiply",
            "test_cases": [
                {"inputs": [2, 3], "expected": 6},
                {"inputs": [4, 5], "expected": 20},
            ],
            "reference_solution": "def multiply(a, b):\n    return a + b",  # Bug: addition instead of multiplication
        },
    }
    is_valid_broken, msg_broken = question_validator.validate_question(broken_coding)
    assert is_valid_broken is False
    assert "failed test validation" in msg_broken.lower()


def test_sql_schema_and_query_validation():
    # 1. Valid SQL with executable schema and query
    valid_sql = {
        "prompt": "Select distinct departments from employees.",
        "question_type": "sql",
        "evaluation_metadata": {
            "schema_ddl": "CREATE TABLE employees (id INT, dept TEXT); INSERT INTO employees VALUES (1, 'IT'), (2, 'HR');",
            "reference_query": "SELECT DISTINCT dept FROM employees ORDER BY dept;",
        },
    }
    is_valid, msg = question_validator.validate_question(valid_sql)
    assert is_valid is True

    # 2. Broken SQL schema (syntax error)
    broken_sql = {
        "prompt": "Select all rows from invalid table.",
        "question_type": "sql",
        "evaluation_metadata": {
            "schema_ddl": "CREATE TABLE bad_table (id INT, INVALID SYNTAX HERE...);",
            "reference_query": "SELECT * FROM bad_table;",
        },
    }
    is_valid_sql_broken, msg_sql_broken = question_validator.validate_question(broken_sql)
    assert is_valid_sql_broken is False
    assert "failed execution" in msg_sql_broken.lower()


def test_batch_generation_and_deduplication_pipeline(db_session):
    # Test batch generation in test environment (uses structured synthesis with validator)
    batch_res = question_bank_service.generate_ai_question_batch(
        skill_or_topic="Algorithms Pipeline",
        category="dsa",
        difficulty="medium",
        question_type="coding",
        batch_size=4,
        db=db_session,
        programming_language="python",
    )
    assert batch_res["requested"] == 4
    assert batch_res["validated_and_saved"] >= 1
    assert "model_metadata" in batch_res

    # Running duplicate batch should prevent duplicates
    second_batch = question_bank_service.generate_ai_question_batch(
        skill_or_topic="Algorithms Pipeline",
        category="dsa",
        difficulty="medium",
        question_type="coding",
        batch_size=4,
        db=db_session,
        programming_language="python",
    )
    assert second_batch["duplicates_prevented"] >= 1


def test_validate_question_by_id_lifecycle(db_session):
    topic = AssessmentTopic(name="Lifecycle Topic", description="Test")
    db_session.add(topic)
    db_session.flush()

    q = Question(
        topic_id=topic.id,
        category="cs_fundamentals",
        question_type="multiple_choice",
        difficulty="easy",
        difficulty_level=2,
        prompt="What is a deterministic finite automaton?",
        options=["A state machine with unambiguous transitions", "A probabilistic Turing machine"],
        evaluation_metadata={
            "correct_answer": "A state machine with unambiguous transitions",
            "explanation": "DFA transitions are deterministic for each input symbol.",
        },
        validation_status="draft",
        is_active=True,
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    # Initial status is draft
    assert q.validation_status == "draft"

    # Validate via service
    is_valid, reason, updated_q = question_bank_service.validate_question_by_id(q.id, db_session)
    assert is_valid is True
    assert updated_q.validation_status == "validated"
