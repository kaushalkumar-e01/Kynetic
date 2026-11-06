from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.assessment import AssessmentTopic, Question, Assessment, AssessmentAttempt
from app.models.skill import Skill, EvidenceRecord
from app.services.capability_service import recalculate_user_capability
from app.services.sandbox import sandbox


DEFAULT_TOPICS_AND_QUESTIONS = [
    {
        "topic": "Python Programming",
        "description": "Python syntax, data types, scoping, memory model, and idiomatic practices.",
        "skill": "Python",
        "questions": [
            {
                "question_type": "multiple_choice",
                "difficulty": "easy",
                "prompt": "What is the output of `bool([])` in Python?",
                "options": ["True", "False", "None", "Error"],
                "evaluation_metadata": {"correct_answer": "False", "explanation": "Empty sequences (lists, tuples, dicts, strings) evaluate to False in Python truth-value testing."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "multiple_choice",
                "difficulty": "medium",
                "prompt": "In Python, which built-in function returns a shallow copy of a list `x`?",
                "options": ["x.copy()", "x.deepcopy()", "copy(x)", "list.clone(x)"],
                "evaluation_metadata": {"correct_answer": "x.copy()", "explanation": "The list method `.copy()` returns a shallow copy. `deepcopy` requires the `copy` module."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "coding",
                "difficulty": "easy",
                "prompt": "Write a function `reverse_string(s: str) -> str` that returns the reversed string.",
                "options": [],
                "evaluation_metadata": {
                    "entry_point": "reverse_string",
                    "test_cases": [
                        {"inputs": ["kynetic"], "expected": "citenyk"},
                        {"inputs": ["hello"], "expected": "olleh"},
                        {"inputs": [""], "expected": ""},
                    ],
                },
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "coding",
                "difficulty": "medium",
                "prompt": "Write a function `two_sum(nums: list, target: int) -> list` that returns indices of the two numbers such that they add up to target. Return sorted indices [i, j].",
                "options": [],
                "evaluation_metadata": {
                    "entry_point": "two_sum",
                    "test_cases": [
                        {"inputs": [[2, 7, 11, 15], 9], "expected": [0, 1]},
                        {"inputs": [[3, 2, 4], 6], "expected": [1, 2]},
                        {"inputs": [[3, 3], 6], "expected": [0, 1]},
                    ],
                },
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "multiple_choice",
                "difficulty": "hard",
                "prompt": "What does Python's GIL (Global Interpreter Lock) specifically prevent?",
                "options": [
                    "Multiple OS threads from executing Python bytecodes concurrently on multiple CPU cores",
                    "Multiple OS processes from running simultaneously",
                    "Memory leaks in circular reference garbage collection",
                    "Deadlocks in asynchronous coroutines",
                ],
                "evaluation_metadata": {"correct_answer": "Multiple OS threads from executing Python bytecodes concurrently on multiple CPU cores", "explanation": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes at once in CPython."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
        ],
    },
    {
        "topic": "Data Structures & Algorithms",
        "description": "Arrays, Hash Tables, Trees, Graphs, Sorting, and Complexity Analysis.",
        "skill": "Data Structures",
        "questions": [
            {
                "question_type": "multiple_choice",
                "difficulty": "easy",
                "prompt": "What is the average time complexity of searching for an element in a balanced Hash Table?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
                "evaluation_metadata": {"correct_answer": "O(1)", "explanation": "Hash tables provide average O(1) time complexity for lookup and insertion with good hash distribution."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "multiple_choice",
                "difficulty": "medium",
                "prompt": "Which algorithm is best suited for finding the shortest path in a weighted graph with non-negative edge weights?",
                "options": ["Dijkstra's Algorithm", "Breadth-First Search", "Bellman-Ford Algorithm", "Depth-First Search"],
                "evaluation_metadata": {"correct_answer": "Dijkstra's Algorithm", "explanation": "Dijkstra's algorithm finds the shortest path in non-negative weighted graphs in O((V + E) log V) with a min-heap."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "multiple_choice",
                "difficulty": "hard",
                "prompt": "What is the worst-case space complexity of a standard recursive Depth First Search on a general graph with V vertices?",
                "options": ["O(V)", "O(E)", "O(V + E)", "O(1)"],
                "evaluation_metadata": {"correct_answer": "O(V)", "explanation": "In the worst case (e.g. a linear chain or deep tree), the call stack can grow up to O(V)."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
        ],
    },
    {
        "topic": "SQL & Relational Databases",
        "description": "SQL queries, relational modeling, indexes, ACID transactions, and normalization.",
        "skill": "SQL",
        "questions": [
            {
                "question_type": "multiple_choice",
                "difficulty": "easy",
                "prompt": "Which SQL clause is used to filter records after aggregation with GROUP BY?",
                "options": ["HAVING", "WHERE", "FILTER", "ORDER BY"],
                "evaluation_metadata": {"correct_answer": "HAVING", "explanation": "HAVING filters groups created by GROUP BY, whereas WHERE filters individual rows before grouping."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
            {
                "question_type": "multiple_choice",
                "difficulty": "medium",
                "prompt": "What type of index is most commonly used in relational databases for equality and range queries?",
                "options": ["B-Tree Index", "Hash Index", "Bitmap Index", "Full-Text Index"],
                "evaluation_metadata": {"correct_answer": "B-Tree Index", "explanation": "B-Trees keep data sorted, allowing logarithmic search, insertion, and efficient range scans."},
                "source_attribution": "Kynetic Original Assessment Bank",
            },
        ],
    },
]


class AssessmentService:
    @staticmethod
    def seed_initial_bank_if_empty(db: Session):
        topic_count = db.query(AssessmentTopic).count()
        if topic_count > 0:
            return

        for topic_data in DEFAULT_TOPICS_AND_QUESTIONS:
            topic = AssessmentTopic(
                name=topic_data["topic"],
                description=topic_data["description"],
            )
            db.add(topic)
            db.flush()

            # Ensure associated skill exists
            skill_name = topic_data.get("skill", topic_data["topic"])
            skill = db.query(Skill).filter(Skill.canonical_name == skill_name).first()
            if not skill:
                db.add(Skill(canonical_name=skill_name, category="concept"))
                db.flush()

            for q_data in topic_data["questions"]:
                q = Question(
                    topic_id=topic.id,
                    question_type=q_data["question_type"],
                    difficulty=q_data["difficulty"],
                    prompt=q_data["prompt"],
                    options=q_data.get("options", []),
                    evaluation_metadata=q_data["evaluation_metadata"],
                    source_attribution=q_data.get("source_attribution"),
                    is_active=True,
                )
                db.add(q)

        db.commit()

    @staticmethod
    def get_adaptive_next_difficulty(attempts: List[AssessmentAttempt]) -> str:
        if not attempts:
            return "easy"

        # Check the last 2 attempts
        recent = attempts[-2:]
        if all(a.is_correct is True for a in recent):
            last_diff = recent[-1].question.difficulty
            if last_diff == "easy":
                return "medium"
            elif last_diff == "medium":
                return "hard"
            return "hard"
        elif all(a.is_correct is False for a in recent):
            last_diff = recent[-1].question.difficulty
            if last_diff == "hard":
                return "medium"
            elif last_diff == "medium":
                return "easy"
            return "easy"

        return recent[-1].question.difficulty

    @staticmethod
    def get_next_question(assessment: Assessment, db: Session) -> Optional[Question]:
        # Gather IDs of questions already attempted in this assessment
        attempted_q_ids = [a.question_id for a in assessment.attempts]

        # Determine target difficulty based on performance
        target_diff = AssessmentService.get_adaptive_next_difficulty(assessment.attempts)

        # Query active questions in selected topics matching target difficulty
        topics = assessment.selected_topics or []
        query = db.query(Question).join(AssessmentTopic).filter(
            Question.is_active.is_(True),
            ~Question.id.in_(attempted_q_ids) if attempted_q_ids else True,
        )
        if topics:
            query = query.filter(AssessmentTopic.name.in_(topics))

        # Try target difficulty first
        q = query.filter(Question.difficulty == target_diff).first()
        if not q:
            # Fallback to any remaining difficulty in the selected topics
            q = query.first()

        return q

    @staticmethod
    def evaluate_quiz_answer(
        assessment: Assessment,
        question: Question,
        user_answer: str,
        user_id: str,
        db: Session,
    ) -> AssessmentAttempt:
        correct_answer = question.evaluation_metadata.get("correct_answer")
        explanation = question.evaluation_metadata.get("explanation", "")

        is_correct = (str(user_answer).strip().lower() == str(correct_answer).strip().lower())
        score = 100.0 if is_correct else 0.0

        attempt = AssessmentAttempt(
            user_id=user_id,
            assessment_id=assessment.id,
            question_id=question.id,
            submitted_answer={"answer": user_answer},
            is_correct=is_correct,
            score=score,
            feedback=f"{'Correct!' if is_correct else 'Incorrect.'} {explanation}",
        )
        db.add(attempt)
        db.flush()

        # Update evidence and capabilities
        AssessmentService._record_assessment_evidence(user_id, question, is_correct, score, db)

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def evaluate_code_submission(
        assessment: Assessment,
        question: Question,
        code_str: str,
        user_id: str,
        db: Session,
    ) -> AssessmentAttempt:
        entry_point = question.evaluation_metadata.get("entry_point", "solution")
        test_cases = question.evaluation_metadata.get("test_cases", [])

        exec_result = sandbox.run_tests(code_str, entry_point, test_cases)
        is_correct = exec_result.get("status") == "passed"
        passed_tests = exec_result.get("passed_tests", 0)
        total_tests = exec_result.get("total_tests", len(test_cases))
        score = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0

        attempt = AssessmentAttempt(
            user_id=user_id,
            assessment_id=assessment.id,
            question_id=question.id,
            submitted_answer={"code": code_str},
            is_correct=is_correct,
            score=score,
            execution_result=exec_result,
            feedback=exec_result.get("error_message") or "All unit tests passed successfully.",
        )
        db.add(attempt)
        db.flush()

        AssessmentService._record_assessment_evidence(user_id, question, is_correct, score, db)

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def _record_assessment_evidence(user_id: str, question: Question, is_correct: bool, score: float, db: Session):
        topic_name = question.topic.name if question.topic else "General"
        # Match skill accurately (first exact, then prefix match)
        skill = db.query(Skill).filter(Skill.canonical_name.ilike(topic_name)).first()
        if not skill:
            skill = db.query(Skill).filter(Skill.canonical_name.ilike(f"%{topic_name.split()[0]}%")).first()
        if not skill:
            skill = Skill(canonical_name=topic_name, category="concept")
            db.add(skill)
            db.flush()

        # Add Demonstrated Assessment Evidence
        evidence = EvidenceRecord(
            user_id=user_id,
            skill_id=skill.id,
            source_type="assessment",
            source_record_id=question.id,
            summary=f"{'Passed' if is_correct else 'Attempted'} {question.difficulty} question on {topic_name} with score {score:.0f}%.",
            confidence=0.85 if is_correct else 0.6,
            quality_metadata={"difficulty": question.difficulty, "is_correct": is_correct, "score": score},
        )
        db.add(evidence)
        db.flush()

        # Recalculate Capability using principled evidence-based scoring
        recalculate_user_capability(user_id=user_id, skill_id=skill.id, db=db)


assessment_service = AssessmentService()

