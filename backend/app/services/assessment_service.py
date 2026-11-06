from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.assessment import AssessmentTopic, Question, Assessment, AssessmentAttempt
from app.models.skill import Skill, EvidenceRecord
from app.services.capability_service import recalculate_user_capability
from app.services.sandbox import sandbox
from app.services.adaptive_engine import adaptive_engine


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
        "topic": "SQL & Database Systems",
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
        # 1. Self-healing table & schema check: ensure all model tables exist and have up-to-date columns
        try:
            from app.models import Base
            Base.metadata.create_all(bind=db.get_bind())

            if db.get_bind().dialect.name == "sqlite":
                result = db.execute(text("PRAGMA table_info(questions)")).fetchall()
                existing_cols = {row[1] for row in result}
                expected_cols = {
                    "category": "VARCHAR(100) DEFAULT 'cs_fundamentals'",
                    "subtopic": "VARCHAR(100)",
                    "difficulty_level": "INTEGER DEFAULT 2",
                    "programming_language": "VARCHAR(50)",
                    "title": "VARCHAR(255)",
                    "source_name": "VARCHAR(100) DEFAULT 'Kynetic Original Bank'",
                    "source_license": "VARCHAR(100) DEFAULT 'CC-BY-4.0'",
                    "source_url": "VARCHAR(255)",
                    "validation_status": "VARCHAR(50) DEFAULT 'validated'",
                    "version": "INTEGER DEFAULT 1",
                }
                for col_name, col_def in expected_cols.items():
                    if col_name not in existing_cols:
                        db.execute(text(f"ALTER TABLE questions ADD COLUMN {col_name} {col_def}"))
                db.commit()
        except Exception:
            db.rollback()

        # 2. Consolidate legacy 'SQL & Relational Databases' topic into canonical 'SQL & Database Systems'
        try:
            legacy_sql = db.query(AssessmentTopic).filter(AssessmentTopic.name == "SQL & Relational Databases").first()
            canonical_sql = db.query(AssessmentTopic).filter(AssessmentTopic.name == "SQL & Database Systems").first()
            if legacy_sql and canonical_sql:
                db.query(Question).filter(Question.topic_id == legacy_sql.id).update({"topic_id": canonical_sql.id})
                db.delete(legacy_sql)
                db.commit()
            elif legacy_sql and not canonical_sql:
                legacy_sql.name = "SQL & Database Systems"
                legacy_sql.description = "Relational database design, ACID compliance, queries, and indexing."
                db.commit()
        except Exception:
            db.rollback()

        topic_count = db.query(AssessmentTopic).count()
        if topic_count == 0:
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
                    diff_str = q_data.get("difficulty", "easy")
                    diff_lvl = adaptive_engine.get_difficulty_level_from_str(diff_str)
                    q = Question(
                        topic_id=topic.id,
                        question_type=q_data["question_type"],
                        difficulty=diff_str,
                        difficulty_level=diff_lvl,
                        title=q_data.get("title") or q_data.get("prompt", "")[:60],
                        prompt=q_data["prompt"],
                        options=q_data.get("options", []),
                        evaluation_metadata=q_data["evaluation_metadata"],
                        source_attribution=q_data.get("source_attribution"),
                        validation_status="validated",
                        is_active=True,
                    )
                    db.add(q)

            db.commit()

        # If question bank has fewer than 100 questions (e.g. fresh installation), ingest expanded catalog
        q_count = db.query(Question).count()
        if q_count < 100:
            AssessmentService.seed_catalog_questions(db)

    @staticmethod
    def seed_catalog_questions(db: Session):
        try:
            from app.services.catalog import get_all_expanded_questions

            def get_or_create_topic(name: str, desc: str, skill_name: str) -> AssessmentTopic:
                t = db.query(AssessmentTopic).filter(AssessmentTopic.name == name).first()
                if not t:
                    t = AssessmentTopic(name=name, description=desc)
                    db.add(t)
                    db.flush()
                s = db.query(Skill).filter(Skill.canonical_name == skill_name).first()
                if not s:
                    db.add(Skill(canonical_name=skill_name, category="concept"))
                    db.flush()
                return t

            topic_map = {
                "dsa": get_or_create_topic("Data Structures & Algorithms", "Algorithmic problem-solving, complexity, and data structures.", "Data Structures"),
                "programming_languages": {
                    "c": get_or_create_topic("C Programming", "Deep C language fundamentals, pointers, and memory model.", "C"),
                    "cpp": get_or_create_topic("C++ Programming", "Modern C++ idioms, STL, templates, and RAII.", "C++"),
                    "java": get_or_create_topic("Java Programming", "Enterprise Java, JVM memory model, and collections.", "Java"),
                    "python": get_or_create_topic("Python Programming", "Pythonic programming, comprehensions, and runtime internals.", "Python"),
                    "javascript": get_or_create_topic("JavaScript Programming", "Modern ECMAScript, event loop, and asynchronous primitives.", "JavaScript"),
                },
                "sql": get_or_create_topic("SQL & Database Systems", "Relational database design, ACID compliance, queries, and indexing.", "SQL"),
                "web_development": get_or_create_topic("Web Development", "Modern fullstack architecture, React, Next.js, and web protocols.", "React"),
                "cs_fundamentals": get_or_create_topic("Computer Science Fundamentals", "Operating systems, computer networks, distributed systems, and DevOps.", "Operating Systems"),
            }

            all_questions = get_all_expanded_questions()
            existing_prompts = set(p[0] for p in db.query(Question.prompt).all())

            for q_data in all_questions:
                prompt = q_data["prompt"]
                if prompt in existing_prompts:
                    continue

                category = q_data.get("category", "cs_fundamentals")
                lang = q_data.get("programming_language")

                if category == "programming_languages" and lang in topic_map["programming_languages"]:
                    topic = topic_map["programming_languages"][lang]
                elif category in topic_map and isinstance(topic_map[category], AssessmentTopic):
                    topic = topic_map[category]
                else:
                    topic = topic_map["cs_fundamentals"]

                diff_str = q_data.get("difficulty", "medium")
                diff_lvl = q_data.get("difficulty_level", 3)

                q = Question(
                    topic_id=topic.id,
                    title=q_data.get("title"),
                    category=category,
                    subtopic=q_data.get("subtopic", "General"),
                    question_type=q_data["question_type"],
                    difficulty=diff_str,
                    difficulty_level=diff_lvl,
                    programming_language=lang,
                    prompt=prompt,
                    options=q_data.get("options", []),
                    evaluation_metadata=q_data["evaluation_metadata"],
                    source_attribution="Kynetic Validated Assessment Bank",
                    source_name="Kynetic Validated Assessment Bank",
                    source_license="CC-BY-4.0",
                    validation_status="validated",
                    version=1,
                    is_active=True,
                )
                db.add(q)
                existing_prompts.add(prompt)

            db.commit()
        except Exception:
            db.rollback()

    @staticmethod
    def get_adaptive_next_difficulty(attempts: List[AssessmentAttempt]) -> str:
        lvl = adaptive_engine.get_adaptive_next_difficulty_level(attempts)
        return adaptive_engine.get_difficulty_str_from_level(lvl)

    @staticmethod
    def get_next_question(assessment: Assessment, db: Session, max_questions: int = 10) -> Optional[Question]:
        return adaptive_engine.get_next_question(assessment, db, max_questions=max_questions)

    @staticmethod
    def evaluate_quiz_answer(
        assessment: Assessment,
        question: Question,
        user_answer: str,
        user_id: str,
        db: Session,
    ) -> AssessmentAttempt:
        q_type = (question.question_type or "multiple_choice").lower()
        meta = question.evaluation_metadata or {}
        explanation = meta.get("explanation", "")
        execution_result = None

        def matches_option_or_letter(user_ans: str, expected_val: str, options: list) -> bool:
            u_clean = str(user_ans).strip().lower()
            exp_clean = str(expected_val).strip().lower()
            if u_clean == exp_clean:
                return True
            # Support letter selection (A, B, C, D) or index (0, 1, 2, 3) or "Option A"
            letter_map = {"a": 0, "b": 1, "c": 2, "d": 3}
            idx = None
            if u_clean in letter_map:
                idx = letter_map[u_clean]
            elif u_clean.isdigit():
                idx = int(u_clean)
            elif u_clean.startswith("option ") and len(u_clean) == 8 and u_clean[7] in letter_map:
                idx = letter_map[u_clean[7]]

            if idx is not None and options and 0 <= idx < len(options):
                opt = options[idx]
                opt_str = opt if isinstance(opt, str) else opt.get("text", "")
                if str(opt_str).strip().lower() == exp_clean:
                    return True
            return False

        if q_type == "sql":
            import sqlite3
            schema_ddl = meta.get("schema_ddl", "")
            ref_query = meta.get("reference_query", "")
            is_correct = False
            score = 0.0

            clean_query = str(user_answer or "").strip()
            if not clean_query:
                is_correct = False
                score = 0.0
                feedback = "Empty SQL query submitted. Please write a query."
                execution_result = {"error": "Empty query"}
            else:
                # Anti-abuse SQL guards
                forbidden_keywords = ["ATTACH", "DETACH", "PRAGMA", "VACUUM"]
                has_forbidden = any(kw in clean_query.upper().split() for kw in forbidden_keywords)
                if has_forbidden:
                    is_correct = False
                    score = 0.0
                    feedback = "Security restriction: Administrative and file-access SQL commands are forbidden."
                    execution_result = {"error": "Forbidden command"}
                else:
                    try:
                        with sqlite3.connect(":memory:") as conn:
                            cur = conn.cursor()
                            if schema_ddl:
                                cur.executescript(schema_ddl)
                            cur.execute(ref_query)
                            expected_rows = cur.fetchall()

                            cur.execute(clean_query)
                            actual_rows = cur.fetchall()

                            if actual_rows == expected_rows:
                                is_correct = True
                                score = 100.0
                                feedback = "Correct! SQL query returned the exact expected result set."
                            else:
                                feedback = f"Output mismatch. Expected {len(expected_rows)} rows, got {len(actual_rows)} rows."
                            execution_result = {"expected_rows": len(expected_rows), "actual_rows": len(actual_rows)}
                    except Exception as e:
                        is_correct = False
                        score = 0.0
                        feedback = f"SQL Execution Error: {str(e)}"
                        execution_result = {"error": str(e)}

        elif q_type == "output_prediction":
            expected = meta.get("expected_output") or meta.get("correct_answer", "")
            is_correct = matches_option_or_letter(user_answer, expected, question.options or [])
            score = 100.0 if is_correct else 0.0
            feedback = f"{'Correct output!' if is_correct else 'Incorrect output.'} {explanation}"

        elif q_type == "debugging":
            expected = meta.get("correct_fix") or meta.get("correct_answer", "")
            is_correct = matches_option_or_letter(user_answer, expected, question.options or [])
            score = 100.0 if is_correct else 0.0
            feedback = f"{'Defect correctly identified and resolved!' if is_correct else 'Incorrect fix.'} {explanation}"

        elif q_type == "conceptual":
            rubric = meta.get("rubric", "")
            key_concepts = meta.get("key_concepts", [])
            user_lower = str(user_answer).lower()
            matched_concepts = [c for c in key_concepts if c.lower() in user_lower]
            if key_concepts:
                ratio = len(matched_concepts) / len(key_concepts)
                score = round(ratio * 100.0, 1)
                is_correct = score >= 50.0
            else:
                score = 80.0 if len(user_answer.strip()) > 30 else 40.0
                is_correct = score >= 50.0

            feedback = f"{'Demonstrated solid conceptual comprehension.' if is_correct else 'Needs deeper explanation.'} Rubric Focus: {rubric}"
            execution_result = {"matched_concepts": matched_concepts, "total_concepts": len(key_concepts)}

        else:  # multiple_choice, multi_select, default
            correct_answer = meta.get("correct_answer") or ""
            is_correct = matches_option_or_letter(user_answer, correct_answer, question.options or [])
            score = 100.0 if is_correct else 0.0
            feedback = f"{'Correct!' if is_correct else 'Incorrect.'} {explanation}"

        attempt = AssessmentAttempt(
            user_id=user_id,
            assessment_id=assessment.id,
            question_id=question.id,
            submitted_answer={"answer": user_answer},
            is_correct=is_correct,
            score=score,
            execution_result=execution_result,
            feedback=feedback,
        )
        db.add(attempt)
        db.flush()

        # Update evidence and capabilities
        AssessmentService._record_assessment_evidence(user_id, question, is_correct, score, db)

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def run_code_test(
        question: Question,
        code_str: str,
    ) -> Dict[str, Any]:
        """Runs candidate code against public/sample test cases only without permanent scoring."""
        meta = question.evaluation_metadata or {}
        entry_point = meta.get("entry_point", "solution")
        test_cases = meta.get("sample_test_cases") or meta.get("test_cases", [])[:2]
        return sandbox.run_tests(code_str, entry_point, test_cases)

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
        status_val = exec_result.get("status")
        is_correct = (status_val == "passed")
        passed_tests = exec_result.get("passed_tests", 0)
        total_tests = exec_result.get("total_tests", len(test_cases))
        score = (passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0

        if status_val == "cheating_detected":
            is_correct = False
            score = 0.0
            feedback = f"Integrity check failed: {exec_result.get('error_message')}"
        elif status_val == "forbidden":
            is_correct = False
            score = 0.0
            feedback = f"Security restriction: {exec_result.get('error_message')}"
        elif status_val == "timeout":
            is_correct = False
            score = 0.0
            feedback = "Time Limit Exceeded: Execution took longer than 3.0 seconds."
        else:
            feedback = exec_result.get("error_message") or "All unit tests passed successfully."

        attempt = AssessmentAttempt(
            user_id=user_id,
            assessment_id=assessment.id,
            question_id=question.id,
            submitted_answer={"code": code_str},
            is_correct=is_correct,
            score=score,
            execution_result=exec_result,
            feedback=feedback,
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
            quality_metadata={"difficulty": question.difficulty, "difficulty_level": question.difficulty_level, "is_correct": is_correct, "score": score},
        )
        db.add(evidence)
        db.flush()

        # Recalculate Capability using principled evidence-based scoring
        recalculate_user_capability(user_id=user_id, skill_id=skill.id, db=db)

        # Check if question has a distinct programming language to also reward
        if question.programming_language and question.programming_language.lower() not in ("none", "", "text"):
            lang_key = question.programming_language.lower()
            lang_names = {
                "python": "Python",
                "javascript": "Javascript",
                "typescript": "Typescript",
                "java": "Java",
                "c": "C",
                "cpp": "C++",
                "sql": "SQL",
            }
            canon_lang = lang_names.get(lang_key, lang_key.capitalize())
            if canon_lang.lower() != skill.canonical_name.lower():
                lang_skill = db.query(Skill).filter(Skill.canonical_name.ilike(canon_lang)).first()
                if not lang_skill:
                    lang_skill = Skill(canonical_name=canon_lang, category="language")
                    db.add(lang_skill)
                    db.flush()
                lang_ev = EvidenceRecord(
                    user_id=user_id,
                    skill_id=lang_skill.id,
                    source_type="assessment",
                    source_record_id=question.id,
                    summary=f"{'Passed' if is_correct else 'Attempted'} {question.difficulty} challenge in {canon_lang} with score {score:.0f}%.",
                    confidence=0.85 if is_correct else 0.6,
                    quality_metadata={
                        "difficulty": question.difficulty,
                        "difficulty_level": question.difficulty_level,
                        "is_correct": is_correct,
                        "score": score,
                    },
                )
                db.add(lang_ev)
                db.flush()
                recalculate_user_capability(user_id=user_id, skill_id=lang_skill.id, db=db)


assessment_service = AssessmentService()

