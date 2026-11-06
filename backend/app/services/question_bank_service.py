import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.config import settings
from app.models.assessment import Question, AssessmentTopic
from app.services.question_validator import question_validator
from app.ai.factory import get_llm_provider

logger = logging.getLogger("kynetic.assessment.bank")


def normalize_text(text: str) -> str:
    return re.sub(r"[^\w\s]", "", (text or "").lower()).strip()


def is_duplicate_prompt(prompt: str, existing_prompts: List[str], threshold: float = 0.82) -> bool:
    """
    Computes token Jaccard similarity to prevent duplicate or near-identical questions.
    """
    tokens = set(re.findall(r"\w+", prompt.lower()))
    if len(tokens) < 3:
        return False

    for ep in existing_prompts:
        ep_tokens = set(re.findall(r"\w+", ep.lower()))
        if len(ep_tokens) < 3:
            continue
        inter = len(tokens & ep_tokens)
        union = len(tokens | ep_tokens)
        if union > 0 and (inter / union) >= threshold:
            return True

    return False


def is_duplicate_question(
    new_q: Dict[str, Any],
    existing_questions: List[Question],
    similarity_threshold: float = 0.80,
) -> bool:
    """
    Multi-layer duplicate detection:
    1. Normalized exact prompt match.
    2. Normalized exact code snippet / reference solution match.
    3. Exact title match within the same subtopic.
    4. Token Jaccard semantic similarity.
    """
    new_prompt = new_q.get("prompt", "")
    new_title = new_q.get("title", "")
    new_meta = new_q.get("evaluation_metadata", {}) or {}
    new_code = str(new_meta.get("code") or new_meta.get("reference_solution") or "").strip()

    norm_new_p = normalize_text(new_prompt)
    norm_new_title = normalize_text(new_title) if new_title else ""
    norm_new_code = normalize_text(new_code) if len(new_code) > 20 else ""

    new_tokens = set(re.findall(r"\w+", new_prompt.lower()))

    for eq in existing_questions:
        eq_meta = eq.evaluation_metadata or {}
        eq_code = str(eq_meta.get("code") or eq_meta.get("reference_solution") or "").strip()

        # 1. Exact prompt normalized match
        if norm_new_p and norm_new_p == normalize_text(eq.prompt):
            return True

        # 2. Exact code normalized match (for questions with significant code)
        if norm_new_code and norm_new_code == normalize_text(eq_code):
            return True

        # 3. Exact title match within same subtopic
        if norm_new_title and eq.title and norm_new_title == normalize_text(eq.title):
            if eq.subtopic == new_q.get("subtopic"):
                return True

        # 4. Token Jaccard similarity on prompt
        if len(new_tokens) >= 4:
            eq_tokens = set(re.findall(r"\w+", eq.prompt.lower()))
            if len(eq_tokens) >= 4:
                inter = len(new_tokens & eq_tokens)
                union = len(new_tokens | eq_tokens)
                if union > 0 and (inter / union) >= similarity_threshold:
                    return True

    return False


class QuestionBankService:
    @staticmethod
    def search_questions(
        db: Session,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        difficulty_level: Optional[int] = None,
        question_type: Optional[str] = None,
        programming_language: Optional[str] = None,
        topic_name: Optional[str] = None,
        search_query: Optional[str] = None,
        validation_status: Optional[str] = "validated",
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
        Generates a batch of technical questions via Gemini 3.5 Flash or Fallback,
        executes deduplication filtering, runs schema & sandbox validation, and persists validated questions.
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

        # Query existing prompts in topic for lexical deduplication
        existing_prompts = [
            q.prompt for q in db.query(Question.prompt).filter(Question.topic_id == topic.id).all()
        ]

        llm = get_llm_provider()
        validated_saved = 0
        rejected_count = 0
        duplicates_prevented = 0
        errors = []

        try:
            # 1. Generate candidate questions using structured provider method
            parsed_list = []
            if hasattr(llm, "generate_question_batch"):
                parsed_list = llm.generate_question_batch(
                    skill_or_topic=skill_or_topic,
                    category=category,
                    difficulty=difficulty,
                    question_type=question_type,
                    batch_size=batch_size,
                    programming_language=programming_language,
                )

            # Fallback to direct prompt if provider returned empty
            if not parsed_list:
                prompt = f"""
You are a Principal Assessment Engineer for Kynetic.
Generate exactly {batch_size} non-trivial technical assessment questions.
Topic: {skill_or_topic}
Category: {category}
Question Type: {question_type}
Target Difficulty: {difficulty} (Level {diff_level} of 6)
Programming Language: {programming_language or 'none'}

Output a strict JSON array of objects matching this schema:
[
  {{
    "prompt": "Detailed problem statement or question",
    "subtopic": "{skill_or_topic}",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "evaluation_metadata": {{
      "correct_answer": "Exact correct answer text",
      "explanation": "Detailed rationale",
      "entry_point": "function_name (for coding)",
      "test_cases": [{{"inputs": [1, 2], "expected": 3}}],
      "reference_solution": "def function_name(a, b): return a + b",
      "buggy_code": "code with bug (for debugging)",
      "correct_fix": "description of fix (for debugging)",
      "schema_ddl": "CREATE TABLE ... (for SQL)",
      "reference_query": "SELECT ... (for SQL)",
      "rubric": "Rubric criteria (for conceptual)",
      "key_concepts": ["concept1", "concept2"]
    }}
  }}
]
Output valid JSON only. Do not wrap in markdown fences.
"""
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

            existing_topic_questions = db.query(Question).filter(
                Question.topic_id == topic.id,
                Question.is_active.is_(True),
            ).all()

            # 2. Iterate, Deduplicate, Validate & Persist
            for item in parsed_list:
                item_prompt = item.get("prompt", "").strip()
                item["question_type"] = question_type
                item["difficulty"] = difficulty
                item["difficulty_level"] = diff_level
                item["category"] = category
                item["programming_language"] = programming_language or "none"

                if is_duplicate_question(item, existing_topic_questions):
                    duplicates_prevented += 1
                    continue

                is_valid, reason = question_validator.validate_question(item)
                if is_valid:
                    item_title = item.get("title") or item.get("evaluation_metadata", {}).get("title")
                    q = Question(
                        topic_id=topic.id,
                        category=category,
                        subtopic=item.get("subtopic", skill_or_topic),
                        question_type=question_type,
                        difficulty=difficulty,
                        difficulty_level=diff_level,
                        programming_language=programming_language,
                        title=item_title,
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
                    existing_topic_questions.append(q)
                    validated_saved += 1
                else:
                    rejected_count += 1
                    errors.append(reason)

            db.commit()
        except Exception as e:
            logger.warning("AI Question generation failed: %s", str(e))
            errors.append(str(e))

        return {
            "requested": batch_size,
            "validated_and_saved": validated_saved,
            "rejected_count": rejected_count,
            "duplicates_prevented": duplicates_prevented,
            "validation_errors": errors[:5],
            "topic": topic.name,
            "model_metadata": {
                "provider": "gemini",
                "model": settings.effective_gemini_model,
            },
        }

    @staticmethod
    def list_questions(
        db: Session,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        difficulty_level: Optional[int] = None,
        question_type: Optional[str] = None,
        programming_language: Optional[str] = None,
        topic_name: Optional[str] = None,
        search_query: Optional[str] = None,
        validation_status: Optional[str] = "validated",
        skip: int = 0,
        limit: int = 50,
    ) -> List[Question]:
        return QuestionBankService.search_questions(
            db=db,
            category=category,
            difficulty=difficulty,
            difficulty_level=difficulty_level,
            question_type=question_type,
            programming_language=programming_language,
            topic_name=topic_name,
            search_query=search_query,
            validation_status=validation_status,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def validate_question_by_id(question_id: str, db: Session) -> Tuple[bool, str, Optional[Question]]:
        """
        Runs full schema, sandbox, and syntax validation on an existing question by ID,
        updating its lifecycle status to 'validated' or 'rejected'.
        """
        q = db.query(Question).filter(Question.id == question_id).first()
        if not q:
            return False, "Question not found", None

        q_dict = {
            "prompt": q.prompt,
            "question_type": q.question_type,
            "options": q.options or [],
            "evaluation_metadata": q.evaluation_metadata or {},
            "programming_language": q.programming_language,
        }
        is_valid, reason = question_validator.validate_question(q_dict)
        q.validation_status = "validated" if is_valid else "rejected"
        db.commit()
        db.refresh(q)
        return is_valid, reason, q


question_bank_service = QuestionBankService()
