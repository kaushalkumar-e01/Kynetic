import pytest
from datetime import datetime, timezone
from app.models.assessment import Assessment, AssessmentAttempt, Question, AssessmentTopic
from app.services.adaptive_engine import adaptive_engine, AdaptiveEngine


def _make_mock_attempt(
    question_id: str,
    diff_lvl: int,
    is_correct: bool,
    score: float,
    created_at_sec: int,
    subtopic: str = "Algorithms",
) -> AssessmentAttempt:
    q = Question(
        id=question_id,
        topic_id="top-mock",
        category="dsa",
        subtopic=subtopic,
        question_type="coding",
        difficulty=AdaptiveEngine.LEVEL_TO_NAME[diff_lvl],
        difficulty_level=diff_lvl,
        prompt=f"Question at level {diff_lvl}",
        options=[],
        evaluation_metadata={"entry_point": "test", "test_cases": []},
        validation_status="validated",
        is_active=True,
    )
    attempt = AssessmentAttempt(
        id=f"att-{question_id}",
        user_id="user_test",
        assessment_id="as_test",
        question_id=question_id,
        is_correct=is_correct,
        score=score,
        created_at=datetime.fromtimestamp(1700000000 + created_at_sec, tz=timezone.utc),
    )
    attempt.question = q
    return attempt


def test_adaptive_difficulty_progression():
    # 1. Starting level with no attempts defaults to Level 2 (Easy)
    assert adaptive_engine.get_adaptive_next_difficulty_level([]) == 2

    # 2. Two consecutive correct answers promote difficulty (+1)
    att1 = _make_mock_attempt("q1", 2, True, 100.0, 10)
    att2 = _make_mock_attempt("q2", 2, True, 100.0, 20)
    next_lvl = adaptive_engine.get_adaptive_next_difficulty_level([att1, att2])
    assert next_lvl == 3  # Level 2 -> Level 3 (Medium)

    # 3. Two consecutive correct at Level 3 promote to Level 4 (Hard)
    att3 = _make_mock_attempt("q3", 3, True, 100.0, 30)
    att4 = _make_mock_attempt("q4", 3, True, 85.0, 40)
    next_lvl_2 = adaptive_engine.get_adaptive_next_difficulty_level([att1, att2, att3, att4])
    assert next_lvl_2 == 4  # Level 3 -> Level 4 (Hard)

    # 4. Two consecutive failures demote difficulty (-1)
    att5 = _make_mock_attempt("q5", 4, False, 20.0, 50)
    att6 = _make_mock_attempt("q6", 4, False, 0.0, 60)
    demoted = adaptive_engine.get_adaptive_next_difficulty_level([att1, att2, att3, att4, att5, att6])
    assert demoted == 3  # Level 4 -> Level 3 (Medium)

    # 5. Boundary Clamping: Cannot exceed Level 6
    att_exp1 = _make_mock_attempt("q_e1", 6, True, 100.0, 70)
    att_exp2 = _make_mock_attempt("q_e2", 6, True, 100.0, 80)
    clamped_top = adaptive_engine.get_adaptive_next_difficulty_level([att_exp1, att_exp2])
    assert clamped_top == 6  # Clamped at 6 (Expert)

    # 6. Boundary Clamping: Cannot demote below Level 1
    att_easy1 = _make_mock_attempt("q_v1", 1, False, 0.0, 90)
    att_easy2 = _make_mock_attempt("q_v2", 1, False, 0.0, 100)
    clamped_bot = adaptive_engine.get_adaptive_next_difficulty_level([att_easy1, att_easy2])
    assert clamped_bot == 1  # Clamped at 1 (Very Easy)


def test_calibrated_mastery_strict_prerequisites():
    """
    CRITICAL REQUIREMENT:
    A user answering only Level 1-2 questions correctly cannot receive 9/10 or 10/10.
    Level 6 (Expert) is strictly required to achieve 9.5-10.0.
    """
    # Candidate A: 100% on Level 1 & Level 2 questions only
    candidate_a_attempts = [
        _make_mock_attempt("qa1", 1, True, 100.0, 10),
        _make_mock_attempt("qa2", 1, True, 100.0, 20),
        _make_mock_attempt("qa3", 2, True, 100.0, 30),
        _make_mock_attempt("qa4", 2, True, 100.0, 40),
        _make_mock_attempt("qa5", 2, True, 100.0, 50),
    ]
    eval_a = adaptive_engine.calculate_calibrated_mastery_score(candidate_a_attempts)
    # Average score is 100%, BUT calibrated mastery score MUST BE capped at 4.5 max
    assert eval_a["average_score"] == 100.0
    assert eval_a["mastery_score"] <= 4.5
    assert eval_a["highest_tier_level"] == 2
    assert eval_a["mastery_band"] in ["Advanced Beginner", "Competent Practitioner"]

    # Candidate B: Successfully solves Level 3 (Medium) questions
    candidate_b_attempts = candidate_a_attempts + [
        _make_mock_attempt("qb1", 3, True, 90.0, 60),
        _make_mock_attempt("qb2", 3, True, 100.0, 70),
    ]
    eval_b = adaptive_engine.calculate_calibrated_mastery_score(candidate_b_attempts)
    assert eval_b["highest_tier_level"] == 3
    assert eval_b["mastery_score"] <= 6.5
    assert eval_b["mastery_score"] > 4.5

    # Candidate C: Solves Level 4 (Hard) and Level 5 (Very Hard)
    candidate_c_attempts = candidate_b_attempts + [
        _make_mock_attempt("qc1", 4, True, 100.0, 80),
        _make_mock_attempt("qc2", 5, True, 95.0, 90),
    ]
    eval_c = adaptive_engine.calculate_calibrated_mastery_score(candidate_c_attempts)
    assert eval_c["highest_tier_level"] == 5
    assert eval_c["mastery_score"] <= 9.0
    assert eval_c["mastery_score"] >= 7.0

    # Candidate D: Solves Level 6 (Expert) challenges
    candidate_d_attempts = candidate_c_attempts + [
        _make_mock_attempt("qd1", 6, True, 100.0, 100),
        _make_mock_attempt("qd2", 6, True, 100.0, 110),
    ]
    eval_d = adaptive_engine.calculate_calibrated_mastery_score(candidate_d_attempts)
    assert eval_d["highest_tier_level"] == 6
    assert eval_d["mastery_score"] >= 9.0
    assert eval_d["mastery_band"] in ["Advanced Specialist", "Master / Principal"]


def test_ability_estimation_and_subtopics():
    attempts = [
        _make_mock_attempt("q1", 2, True, 100.0, 10, subtopic="Arrays"),
        _make_mock_attempt("q2", 3, True, 80.0, 20, subtopic="Dynamic Programming"),
        _make_mock_attempt("q3", 4, False, 40.0, 30, subtopic="Graphs"),
    ]
    ability = adaptive_engine.estimate_user_ability(attempts)
    assert 1.0 <= ability["ability_theta"] <= 6.0
    assert ability["highest_tier_passed"] == 3
    assert ability["highest_tier_attempted"] == 4
    assert "Arrays" in ability["subtopic_abilities"]
    assert "Dynamic Programming" in ability["subtopic_abilities"]
    assert "Graphs" in ability["subtopic_abilities"]
    assert ability["subtopic_abilities"]["Arrays"] == 100.0


def test_adaptive_question_selection_flow(db_session):
    topic = AssessmentTopic(name="Adaptive Testing Topic", description="Test")
    db_session.add(topic)
    db_session.flush()

    # Seed 1 question of each difficulty (Levels 1 to 6)
    for lvl in range(1, 7):
        diff_name = AdaptiveEngine.LEVEL_TO_NAME[lvl]
        q = Question(
            topic_id=topic.id,
            category="dsa",
            subtopic="Trees",
            question_type="coding",
            difficulty=diff_name,
            difficulty_level=lvl,
            prompt=f"DSA question at level {lvl}",
            options=[],
            evaluation_metadata={"entry_point": "solve", "test_cases": []},
            validation_status="validated",
            is_active=True,
        )
        db_session.add(q)
    db_session.flush()

    assessment = Assessment(
        user_id="test_user_adaptive",
        title="Adaptive Selection Test",
        mode="coding",
        selected_topics=["Adaptive Testing Topic"],
        status="in_progress",
    )
    db_session.add(assessment)
    db_session.flush()

    # Initial question should match baseline Level 2 (Easy)
    first_q = adaptive_engine.get_next_question(assessment, db_session)
    assert first_q is not None
    assert first_q.difficulty_level == 2

    # Simulate 2 consecutive correct answers at Level 2
    att1 = AssessmentAttempt(
        user_id="test_user_adaptive",
        assessment_id=assessment.id,
        question_id=first_q.id,
        is_correct=True,
        score=100.0,
    )
    att1.question = first_q
    assessment.attempts.append(att1)

    # Next attempt also Level 2
    att2 = AssessmentAttempt(
        user_id="test_user_adaptive",
        assessment_id=assessment.id,
        question_id=first_q.id,
        is_correct=True,
        score=100.0,
    )
    att2.question = first_q
    assessment.attempts.append(att2)

    # Next question must be promoted to Level 3 (Medium)
    next_q = adaptive_engine.get_next_question(assessment, db_session)
    assert next_q is not None
    assert next_q.difficulty_level == 3

