import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.assessment import AssessmentTopic, Question
from app.services.question_validator import question_validator
from app.ai import get_llm_provider
from app.core.config import settings

logger = logging.getLogger("kynetic.assessment.bank")


class QuestionBankService:
    @staticmethod
    def list_questions(
        db: Session,
        category: Optional[str] = None,
        topic_name: Optional[str] = None,
        difficulty: Optional[str] = None,
        difficulty_level: Optional[int] = None,
        question_type: Optional[str] = None,
        programming_language: Optional[str] = None,
        validation_status: Optional[str] = "validated",
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Question]:
        query = db.query(Question).filter(Question.is_active.is_(True))

        if validation_status:
            query = query.filter(Question.validation_status == validation_status)
        if category:
            query = query.filter(Question.category == category)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if difficulty_level:
            query = query.filter(Question.difficulty_level == difficulty_level)
        if question_type:
            query = query.filter(Question.question_type == question_type)
        if programming_language:
            query = query.filter(Question.programming_language == programming_language)
        if topic_name:
            query = query.join(AssessmentTopic).filter(AssessmentTopic.name.ilike(f"%{topic_name}%"))
        if search_query:
            query = query.filter(Question.prompt.ilike(f"%{search_query}%"))

        return query.order_by(desc(Question.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_question_count(
        db: Session,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None,
        validation_status: Optional[str] = "validated",
    ) -> int:
        query = db.query(Question).filter(Question.is_active.is_(True))
        if validation_status:
            query = query.filter(Question.validation_status == validation_status)
        if category:
            query = query.filter(Question.category == category)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if question_type:
            query = query.filter(Question.question_type == question_type)
        return query.count()

    @staticmethod
    def generate_ai_question_batch(
        skill_or_topic: str,
        category: str,
        difficulty: str,
        question_type: str,
        batch_size: int,
        db: Session,
        programming_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a batch of 10-25 questions via Google Gemini, runs them
        through QuestionValidator, and stores only validated questions into SQLite.
        """
        batch_size = max(1, min(25, batch_size))
        difficulty_map = {
            "very_easy": 1,
            "easy": 2,
            "medium": 3,
            "hard": 4,
            "very_hard": 5,
            "expert": 6,
        }
        diff_level = difficulty_map.get(difficulty.lower(), 3)

        topic = db.query(AssessmentTopic).filter(AssessmentTopic.name.ilike(f"%{skill_or_topic}%")).first()
        if not topic:
            topic = AssessmentTopic(name=skill_or_topic, description=f"Technical assessments for {skill_or_topic}")
            db.add(topic)
            db.flush()

        llm = get_llm_provider()
        prompt = f"""
        You are a Principal Technical Assessment Architect for Kynetic.
        Generate exactly {batch_size} high-quality, non-trivial technical questions.
        Topic: {skill_or_topic}
        Category: {category}
        Question Type: {question_type}
        Target Difficulty: {difficulty} (Level {diff_level} of 6)
        Programming Language: {programming_language or 'none'}

        Output a strict JSON array of question objects matching this schema:
        [
          {{
            "prompt": "Detailed problem statement or question",
            "subtopic": "Specific subtopic or algorithm name",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "evaluation_metadata": {{
              "correct_answer": "Exact correct option string (for MCQ/output prediction)",
              "explanation": "Concrete technical explanation",
              "entry_point": "function_name (for coding)",
              "test_cases": [{{"inputs": [1, 2], "expected": 3}}],
              "reference_solution": "def function_name(a, b): return a + b",
              "buggy_code": "code with bug (for debugging)",
              "correct_fix": "description of fix (for debugging)",
              "schema_ddl": "CREATE TABLE and INSERT statements (for SQL)",
              "reference_query": "SELECT ... (for SQL)",
              "rubric": "Rubric criteria (for conceptual)"
            }}
          }}
        ]
        Do NOT output markdown fences or prose, only valid JSON.
        """

        validated_saved = 0
        rejected_count = 0
        errors = []

        try:
            # Generate using Gemini provider or fallback
            raw_response = ""
            if hasattr(llm, "_execute_with_retry"):
                raw_response = llm._execute_with_retry(prompt)
            else:
                raw_response = llm.generate_chat_response(prompt, {})

            cleaned = (raw_response or "").strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            parsed_list = json.loads(cleaned.strip())
            if not isinstance(parsed_list, list):
                parsed_list = [parsed_list]

            for item in parsed_list:
                item["question_type"] = question_type
                item["difficulty"] = difficulty
                item["difficulty_level"] = diff_level
                item["category"] = category
                item["programming_language"] = programming_language or "none"

                is_valid, reason = question_validator.validate_question(item)
                if is_valid:
                    q = Question(
                        topic_id=topic.id,
                        category=category,
                        subtopic=item.get("subtopic", skill_or_topic),
                        question_type=question_type,
                        difficulty=difficulty,
                        difficulty_level=diff_level,
                        programming_language=programming_language,
                        prompt=item["prompt"],
                        options=item.get("options", []),
                        evaluation_metadata=item.get("evaluation_metadata", {}),
                        source_attribution="AI-Generated via Google Gemini",
                        source_name="Google Gemini",
                        source_license="Proprietary Generated",
                        validation_status="validated",
                        version=1,
                        is_active=True,
                    )
                    db.add(q)
                    validated_saved += 1
                else:
                    rejected_count += 1
                    errors.append(reason)

            db.commit()
        except Exception as e:
            logger.warning("AI Question generation failed or fell back: %s", str(e))
            errors.append(str(e))

        return {
            "requested": batch_size,
            "validated_and_saved": validated_saved,
            "rejected_count": rejected_count,
            "validation_errors": errors[:5],
            "topic": topic.name,
            "model_metadata": {
                "provider": "gemini",
                "model": settings.effective_gemini_model,
            },
        }


question_bank_service = QuestionBankService()

