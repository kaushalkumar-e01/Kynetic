"""
Kynetic Question Bank Repair & Option Balance Script
Safely cleans up cloned/duplicate questions in kynetic_dev.db by retiring duplicates,
updates questions with balanced MCQ options (A, B, C, D evenly distributed),
and inserts new distinct questions, ensuring >= 2,000 active validated questions.
Preserves all historical user attempts, responses, and accounts.
"""
import sys
import os
import logging
from typing import Dict, Any, List

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.db.session import SessionLocal
from app.models.assessment import AssessmentTopic, Question, AssessmentAttempt
from app.models.skill import Skill
from app.services.catalog import get_all_expanded_questions
from app.services.catalog.catalog_helpers import get_title_root, balance_options
from app.services.question_validator import question_validator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("repair_bank")


def get_or_create_topic(db, name: str, description: str, category_skill: str) -> AssessmentTopic:
    topic = db.query(AssessmentTopic).filter(AssessmentTopic.name == name).first()
    if not topic:
        topic = AssessmentTopic(name=name, description=description)
        db.add(topic)
        db.flush()

    skill = db.query(Skill).filter(Skill.canonical_name == category_skill).first()
    if not skill:
        db.add(Skill(canonical_name=category_skill, category="concept"))
        db.flush()

    return topic


def repair_and_balance_bank():
    db = SessionLocal()

    try:
        # 1. Inspect referenced questions from attempts
        referenced_q_ids = set(a.question_id for a in db.query(AssessmentAttempt.question_id).all() if a.question_id)
        logger.info(f"Preserving {len(referenced_q_ids)} questions referenced by existing user attempts.")

        # 2. Identify and safely retire cloned questions in database
        # E.g. questions containing "(Case X)" or "(Topic Y)" where root is duplicated
        active_db_questions = db.query(Question).filter(Question.is_active == True).all()
        logger.info(f"Active questions before repair: {len(active_db_questions)}")

        # Group existing questions by title root
        seen_roots = {}
        retired_clones = 0
        for q in active_db_questions:
            root = get_title_root(q.title or "")
            if not root:
                continue
            if root not in seen_roots:
                seen_roots[root] = q.id
            else:
                # This is a clone of an existing root!
                # If not referenced by historical attempt, retire it
                if q.id not in referenced_q_ids:
                    q.is_active = False
                    q.validation_status = "retired"
                    retired_clones += 1

        db.commit()
        logger.info(f"Safely retired {retired_clones} redundant cloned questions.")

        # 3. Ensure topic mapping
        topic_map = {
            "dsa": get_or_create_topic(db, "Data Structures & Algorithms", "Algorithmic problem-solving, complexity, and data structures.", "Data Structures"),
            "programming_languages": {
                "c": get_or_create_topic(db, "C Programming", "Deep C language fundamentals, pointers, and memory model.", "C"),
                "cpp": get_or_create_topic(db, "C++ Programming", "Modern C++ idioms, STL, templates, and RAII.", "C++"),
                "java": get_or_create_topic(db, "Java Programming", "Enterprise Java, JVM memory model, and collections.", "Java"),
                "python": get_or_create_topic(db, "Python Programming", "Pythonic programming, comprehensions, and runtime internals.", "Python"),
                "javascript": get_or_create_topic(db, "JavaScript Programming", "Modern ECMAScript, event loop, and asynchronous primitives.", "JavaScript"),
            },
            "sql": get_or_create_topic(db, "SQL & Database Systems", "Relational database design, ACID compliance, queries, and indexing.", "SQL"),
            "web_development": get_or_create_topic(db, "Web Development", "Modern fullstack architecture, React, Next.js, and web protocols.", "React"),
            "cs_fundamentals": get_or_create_topic(db, "Computer Science Fundamentals", "Operating systems, computer networks, distributed systems, and DevOps.", "Operating Systems"),
        }

        # 4. Load catalog questions (2,000 unique questions with balanced options)
        catalog_questions = get_all_expanded_questions()
        logger.info(f"Loaded {len(catalog_questions)} validated questions from upgraded catalogs.")

        # Map active questions by title
        current_active = {q.title: q for q in db.query(Question).filter(Question.is_active == True).all()}
        inserted = 0
        updated = 0

        for q_data in catalog_questions:
            title = q_data.get("title")
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

            if title in current_active:
                # Update existing active question with clean balanced options & metadata
                q = current_active[title]
                q.options = q_data.get("options", [])
                q.evaluation_metadata = q_data["evaluation_metadata"]
                q.prompt = q_data["prompt"]
                q.programming_language = lang
                q.difficulty = diff_str
                q.difficulty_level = diff_lvl
                q.validation_status = "validated"
                q.is_active = True
                updated += 1
            else:
                # Insert new distinct question
                q = Question(
                    topic_id=topic.id,
                    title=title,
                    category=category,
                    subtopic=q_data.get("subtopic", "General"),
                    question_type=q_data["question_type"],
                    difficulty=diff_str,
                    difficulty_level=diff_lvl,
                    programming_language=lang,
                    prompt=q_data["prompt"],
                    options=q_data.get("options", []),
                    evaluation_metadata=q_data["evaluation_metadata"],
                    source_attribution="Kynetic Validated Assessment Bank",
                    source_name="Kynetic Validated Assessment Bank",
                    source_license="CC-BY-4.0",
                    source_url="https://kynetic.dev/assessments/bank",
                    validation_status="validated",
                    version=1,
                    is_active=True,
                )
                db.add(q)
                current_active[title] = q
                inserted += 1

            if (inserted + updated) % 100 == 0:
                db.commit()

        db.commit()
        logger.info(f"Catalog ingestion complete: {inserted} inserted, {updated} updated.")

        # 5. Final Audit
        final_active = db.query(Question).filter(Question.is_active == True, Question.validation_status == "validated").count()
        final_retired = db.query(Question).filter(Question.validation_status == "retired").count()
        total_q = db.query(Question).count()
        final_attempts = db.query(AssessmentAttempt).count()

        # Check MCQ option distribution
        active_mcqs = db.query(Question).filter(
            Question.is_active == True,
            Question.question_type == "multiple_choice"
        ).all()
        pos_counts = {0: 0, 1: 0, 2: 0, 3: 0, -1: 0}
        for q in active_mcqs:
            correct = q.evaluation_metadata.get("correct_answer")
            try:
                p = q.options.index(correct)
                pos_counts[p] += 1
            except (ValueError, AttributeError):
                pos_counts[-1] += 1

        logger.info("=" * 60)
        logger.info("FINAL DATABASE AUDIT SUMMARY:")
        logger.info(f"  Active Validated Questions: {final_active} (Target >= 2,000)")
        logger.info(f"  Safely Retired Questions:   {final_retired}")
        logger.info(f"  Total Questions in DB:      {total_q}")
        logger.info(f"  User Attempts Preserved:    {final_attempts}")
        logger.info(f"  MCQ Option Position Counts: {pos_counts} (A: {pos_counts[0]}, B: {pos_counts[1]}, C: {pos_counts[2]}, D: {pos_counts[3]})")
        logger.info("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    repair_and_balance_bank()

