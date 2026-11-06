from app.services.question_validator import question_validator
from app.services.question_bank_builder import question_bank_builder
from app.services.question_bank_service import question_bank_service
from app.api.v1.endpoints.assessments import get_question_bank_statistics, search_question_bank


def test_question_validator_types():
    # 1. Valid MCQ
    valid_mcq = {
        "prompt": "What is the Big-O time complexity of accessing an array element by index?",
        "question_type": "multiple_choice",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "evaluation_metadata": {"correct_answer": "O(1)", "explanation": "Direct indexing takes constant time."},
    }
    is_valid, msg = question_validator.validate_question(valid_mcq)
    assert is_valid is True

    # 2. Invalid MCQ (answer not in options)
    invalid_mcq = {
        "prompt": "What is the Big-O time complexity of binary search?",
        "question_type": "multiple_choice",
        "options": ["O(1)", "O(n)"],
        "evaluation_metadata": {"correct_answer": "O(log n)", "explanation": "Logarithmic time."},
    }
    is_valid, msg = question_validator.validate_question(invalid_mcq)
    assert is_valid is False

    # 3. Valid Coding with reference solution
    valid_coding = {
        "prompt": "Implement function `is_even(n: int) -> bool` returning True if n is even.",
        "question_type": "coding",
        "programming_language": "python",
        "evaluation_metadata": {
            "entry_point": "is_even",
            "test_cases": [
                {"inputs": [4], "expected": True},
                {"inputs": [7], "expected": False},
                {"inputs": [0], "expected": True},
            ],
            "reference_solution": "def is_even(n):\n    return n % 2 == 0",
        },
    }
    is_valid, msg = question_validator.validate_question(valid_coding)
    assert is_valid is True

    # 4. Valid SQL Question
    valid_sql = {
        "prompt": "Select all active customers ordered by signup date.",
        "question_type": "sql",
        "evaluation_metadata": {
            "schema_ddl": "CREATE TABLE customers (id INT, name TEXT, active INT); INSERT INTO customers VALUES (1, 'Eve', 1);",
            "reference_query": "SELECT * FROM customers WHERE active = 1;",
        },
    }
    is_valid, msg = question_validator.validate_question(valid_sql)
    assert is_valid is True


def test_question_bank_statistics_and_filtering(db_session):
    # Ensure bank is seeded
    stats = question_bank_builder.seed_2000_questions(db_session, force=False)
    assert stats["total_questions"] >= 2000
    assert stats["validated_questions"] >= 2000

    # Test stats endpoint function
    stats_resp = get_question_bank_statistics(db=db_session)
    assert stats_resp.total_questions >= 2000
    assert "dsa" in stats_resp.by_category
    assert "programming_languages" in stats_resp.by_category
    assert "sql" in stats_resp.by_category
    assert "web_development" in stats_resp.by_category
    assert "cs_fundamentals" in stats_resp.by_category

    # Verify 6 difficulty tiers present
    for diff in ["very_easy", "easy", "medium", "hard", "very_hard", "expert"]:
        assert diff in stats_resp.by_difficulty
        assert stats_resp.by_difficulty[diff] > 0

    # Test filtering by category and difficulty
    dsa_questions = search_question_bank(
        category="dsa",
        difficulty="medium",
        limit=10,
        db=db_session,
    )
    assert len(dsa_questions) > 0
    assert all(q.category == "dsa" for q in dsa_questions)
    assert all(q.difficulty == "medium" for q in dsa_questions)


def test_ai_question_generation_batch(db_session):
    # Test batch generation in test environment (uses Fallback / mock)
    batch_res = question_bank_service.generate_ai_question_batch(
        skill_or_topic="Python Programming",
        category="programming_languages",
        difficulty="easy",
        question_type="multiple_choice",
        batch_size=5,
        db=db_session,
        programming_language="python",
    )
    assert batch_res["requested"] == 5
    assert "topic" in batch_res

