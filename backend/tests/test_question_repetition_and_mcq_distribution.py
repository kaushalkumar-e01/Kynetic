"""
Comprehensive Verification Tests for:
1. No Repeated Questions After Submissions (Unique IDs & Prompts)
2. Semantic Deduplication & Non-Clone Selection in Adaptive Engine
3. Balanced MCQ Correct Answer Distribution Across A, B, C, D
4. Option Letter & Text Answer Evaluation Accuracy
5. Question Formatting Integrity & Markdown Artifact Elimination
6. Graceful Pool Exhaustion without Repeats
"""
import pytest
from app.models.user import User
from app.models.assessment import Assessment, AssessmentAttempt, Question, AssessmentTopic
from app.services.adaptive_engine import adaptive_engine
from app.services.assessment_service import assessment_service
from app.services.catalog import get_all_expanded_questions
from app.api.v1.endpoints.assessments import serialize_public_question


def create_mock_user(db_session) -> User:
    user = User(email="testuser@kynetic.dev", password_hash="hashed_pw_123", account_status="active")
    db_session.add(user)
    db_session.flush()
    return user


def create_mock_topic(db_session, name="Python Programming") -> AssessmentTopic:
    topic = db_session.query(AssessmentTopic).filter(AssessmentTopic.name == name).first()
    if not topic:
        topic = AssessmentTopic(name=name, description=f"{name} topics")
        db_session.add(topic)
        db_session.flush()
    return topic


def test_mcq_option_distribution_balanced():
    """Verify active MCQs in the expanded catalog have balanced correct answer positions across A, B, C, D."""
    all_qs = get_all_expanded_questions()
    mcqs = [q for q in all_qs if q["question_type"] == "multiple_choice"]
    assert len(mcqs) >= 100, "Should have at least 100 MCQs in catalog"

    pos_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for q in mcqs:
        ans = q["evaluation_metadata"]["correct_answer"]
        assert ans in q["options"], f"Correct answer '{ans}' must be present in options {q['options']}"
        pos = q["options"].index(ans)
        pos_counts[pos] += 1

    total = len(mcqs)
    for pos, count in pos_counts.items():
        ratio = count / total
        letter = ["A", "B", "C", "D"][pos]
        # Each position should be between 20% and 30% (ideally ~25%)
        assert 0.20 <= ratio <= 0.30, f"Option {letter} ratio {ratio:.2f} is outside balanced 20-30% range"


def test_no_repeated_questions_across_submissions(db_session):
    """
    Verify that advancing through an assessment generates a completely unique question
    after every single submission, with no duplicate IDs or identical prompts.
    """
    user = create_mock_user(db_session)
    topic = create_mock_topic(db_session, "General CS")

    # Add 10 realistic distinct questions with unique topics and prompts
    distinct_specs = [
        ("Kadane Subarray Maximum", "Compute the maximum contiguous subarray sum in linear time.", "O(N)"),
        ("Dijkstra Shortest Path", "Find single-source shortest paths in a non-negative weighted graph.", "Min-heap"),
        ("BST Inorder Traversal", "Traverse a binary search tree in sorted order using DFS.", "Left-Root-Right"),
        ("Kahn Topological Sort", "Determine if a directed graph contains a cycle using in-degrees.", "Queue"),
        ("Levenshtein Edit Distance", "Compute minimum edit operations to transform string A into string B.", "DP Matrix"),
        ("LRU Cache Eviction", "Evict least recently used entries when cache capacity is exceeded.", "Doubly Linked List"),
        ("Rabin-Karp Substring Search", "Find substring occurrences using rolling polynomial hash.", "Rolling Hash"),
        ("Trie Prefix Autocomplete", "Search all keys matching a given prefix efficiently.", "Trie Nodes"),
    ]

    for i, (p_title, p_desc, p_ans) in enumerate(distinct_specs, 1):
        q = Question(
            topic_id=topic.id,
            title=p_title,
            prompt=p_desc,
            question_type="multiple_choice",
            difficulty="medium",
            difficulty_level=3,
            options=[p_ans, "Alternative X", "Alternative Y", "Alternative Z"],
            evaluation_metadata={"correct_answer": p_ans},
            is_active=True,
            validation_status="validated",
        )
        db_session.add(q)
    db_session.commit()

    assessment = Assessment(
        user_id=user.id,
        title="Repetition Elimination Test",
        mode="quiz",
        selected_topics=[topic.name],
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    seen_q_ids = set()
    seen_prompts = set()

    for step in range(6):
        next_q = adaptive_engine.get_next_question(assessment, db_session, max_questions=10)
        assert next_q is not None, f"Expected a valid question at step {step+1}"

        # Check 1: Unique ID - Never show the same question ID twice in one assessment
        assert next_q.id not in seen_q_ids, f"Step {step+1}: Question ID {next_q.id} was repeated!"
        seen_q_ids.add(next_q.id)

        # Check 2: Unique Prompt - Never show semantically identical questions
        assert next_q.prompt not in seen_prompts, f"Step {step+1}: Prompt was repeated: {next_q.prompt[:60]}"
        seen_prompts.add(next_q.prompt)

        # Submit an answer to simulate real progression
        meta = next_q.evaluation_metadata or {}
        ans = meta.get("correct_answer") or meta.get("correct_fix") or "test_answer"
        assessment_service.evaluate_quiz_answer(
            assessment=assessment,
            question=next_q,
            user_answer=ans,
            user_id=user.id,
            db=db_session,
        )
        db_session.refresh(assessment)

    assert len(seen_q_ids) == 6, "Must have presented 6 completely unique questions"


def test_semantic_deduplication_rejects_clones(db_session):
    """Verify that AdaptiveEngine detects and rejects questions with identical semantic roots."""
    user = create_mock_user(db_session)
    topic = create_mock_topic(db_session, "C Programming")

    # Create two questions with identical root title and identical code
    q1 = Question(
        topic_id=topic.id,
        title="C Dangling Pointer & Stack Scope Defect (Case 1)",
        prompt="Identify the defect in get_stack_buffer:\n```c\nint* get_stack_buffer() { int a = 1; return &a; }\n```",
        question_type="debugging",
        difficulty="hard",
        difficulty_level=4,
        programming_language="c",
        options=["Stack variable address returned", "Missing semicolon", "Invalid type", "Malloc error"],
        evaluation_metadata={"correct_fix": "Stack variable address returned", "code": "int* get_stack_buffer() { int a = 1; return &a; }"},
        is_active=True,
        validation_status="validated",
    )
    q2 = Question(
        topic_id=topic.id,
        title="C Dangling Pointer & Stack Scope Defect (Case 2)",
        prompt="Identify the defect in get_stack_buffer:\n```c\nint* get_stack_buffer() { int a = 2; return &a; }\n```",
        question_type="debugging",
        difficulty="hard",
        difficulty_level=4,
        programming_language="c",
        options=["Stack variable address returned", "Wrong return", "Null pointer", "Double free"],
        evaluation_metadata={"correct_fix": "Stack variable address returned", "code": "int* get_stack_buffer() { int a = 2; return &a; }"},
        is_active=True,
        validation_status="validated",
    )
    # Third completely different question
    q3 = Question(
        topic_id=topic.id,
        title="C String Null Terminator Flaw",
        prompt="Identify why printf overruns on strncpy without null terminator:\n```c\nchar b[5]; strncpy(b, s, 5);\n```",
        question_type="debugging",
        difficulty="hard",
        difficulty_level=4,
        programming_language="c",
        options=["Missing null terminator", "Double free", "Stack leak", "Type mismatch"],
        evaluation_metadata={"correct_fix": "Missing null terminator", "code": "char b[5]; strncpy(b, s, 5);"},
        is_active=True,
        validation_status="validated",
    )
    db_session.add_all([q1, q2, q3])
    db_session.commit()

    assessment = Assessment(
        user_id=user.id,
        title="Deduplication Verification",
        mode="quiz",
        selected_topics=[topic.name],
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.commit()

    # Attempt q1
    attempt = AssessmentAttempt(
        user_id=user.id,
        assessment_id=assessment.id,
        question_id=q1.id,
        submitted_answer={"answer": "Stack variable address returned"},
        is_correct=True,
        score=100.0,
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(assessment)

    # Next question selection should reject q2 because it shares the same semantic root and code
    next_q = adaptive_engine.get_next_question(assessment, db_session, max_questions=5)
    assert next_q is not None
    assert next_q.id != q1.id, "Cannot return q1 again"
    assert next_q.id != q2.id, "q2 should be rejected as a semantic duplicate of q1"
    assert next_q.id == q3.id, "q3 should be selected as the distinct valid question"


def test_answer_evaluation_handles_both_text_and_letters(db_session):
    """
    Verify that evaluate_quiz_answer correctly scores 100% when submitting:
      - The exact answer text
      - The option letter ('B', 'C', 'b', 'Option B')
      - And scores 0% for an incorrect choice.
    """
    user = create_mock_user(db_session)
    topic = create_mock_topic(db_session, "Memory")
    # Correct answer is at index 1 ("Option B")
    q = Question(
        topic_id=topic.id,
        title="Memory Allocation Semantics Test",
        prompt="Which function zeroes memory bytes?",
        question_type="multiple_choice",
        difficulty="medium",
        difficulty_level=3,
        options=["malloc()", "calloc()", "realloc()", "alloca()"],
        evaluation_metadata={"correct_answer": "calloc()", "explanation": "calloc clears memory to 0."},
        is_active=True,
        validation_status="validated",
    )
    db_session.add(q)
    db_session.commit()

    assessment = Assessment(user_id=user.id, title="Eval Test", mode="quiz", status="in_progress")
    db_session.add(assessment)
    db_session.commit()

    # 1. Exact string match
    att1 = assessment_service.evaluate_quiz_answer(assessment, q, "calloc()", user.id, db_session)
    assert att1.is_correct is True
    assert att1.score == 100.0

    # 2. Option letter "B" (uppercase)
    att2 = assessment_service.evaluate_quiz_answer(assessment, q, "B", user.id, db_session)
    assert att2.is_correct is True
    assert att2.score == 100.0

    # 3. Option letter "b" (lowercase)
    att3 = assessment_service.evaluate_quiz_answer(assessment, q, "b", user.id, db_session)
    assert att3.is_correct is True
    assert att3.score == 100.0

    # 4. "Option B"
    att4 = assessment_service.evaluate_quiz_answer(assessment, q, "Option B", user.id, db_session)
    assert att4.is_correct is True
    assert att4.score == 100.0

    # 5. Wrong letter "A"
    att5 = assessment_service.evaluate_quiz_answer(assessment, q, "A", user.id, db_session)
    assert att5.is_correct is False
    assert att5.score == 0.0


def test_serialize_public_question_cleans_markdown_artifacts(db_session):
    """Verify that serialize_public_question removes raw '### ' prefix and separates title from prompt."""
    topic = create_mock_topic(db_session, "Python")
    q = Question(
        topic_id=topic.id,
        title="### Clean Header Extraction",
        prompt="### Clean Header Extraction\n\nWhat is the output of `bool(1)` in Python?",
        question_type="multiple_choice",
        difficulty="easy",
        difficulty_level=2,
        options=["True", "False"],
        evaluation_metadata={"correct_answer": "True"},
        is_active=True,
        validation_status="validated",
    )
    db_session.add(q)
    db_session.commit()

    res = serialize_public_question(q)
    assert not res.title.startswith("###"), f"Title should be stripped of raw markdown headers: {res.title}"
    assert not res.prompt.startswith("###"), f"Prompt should not duplicate raw header: {res.prompt}"
    assert res.title == "Clean Header Extraction"
    assert "What is the output of `bool(1)` in Python?" in res.prompt


def test_graceful_pool_exhaustion_returns_none(db_session):
    """Verify that when all available questions have been attempted, AdaptiveEngine returns None and never repeats."""
    user = create_mock_user(db_session)
    topic = create_mock_topic(db_session, "Small Pool")

    q = Question(
        topic_id=topic.id,
        title="Single Unique Problem",
        prompt="Only one question in pool.",
        question_type="multiple_choice",
        difficulty="easy",
        difficulty_level=2,
        options=["A", "B", "C", "D"],
        evaluation_metadata={"correct_answer": "A"},
        is_active=True,
        validation_status="validated",
    )
    db_session.add(q)
    db_session.commit()

    assessment = Assessment(
        user_id=user.id,
        title="Exhaustion Test",
        mode="quiz",
        selected_topics=[topic.name],
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.commit()

    # Step 1: First question returned
    q1 = adaptive_engine.get_next_question(assessment, db_session, max_questions=5)
    assert q1 is not None
    assert q1.id == q.id

    # Record attempt
    assessment_service.evaluate_quiz_answer(assessment, q1, "A", user.id, db_session)
    db_session.refresh(assessment)

    # Step 2: Pool exhausted -> should return None, NEVER repeat q1!
    q2 = adaptive_engine.get_next_question(assessment, db_session, max_questions=5)
    assert q2 is None, "Should gracefully return None when question pool is exhausted, not repeat!"
