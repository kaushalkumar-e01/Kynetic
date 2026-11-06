import math
import re
import random
from typing import Dict, Any, List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.assessment import Assessment, AssessmentAttempt, Question, AssessmentTopic


class AdaptiveEngine:
    """
    Kynetic Adaptive Assessment Engine (6 Difficulty Tiers)
    
    Difficulty Tiers:
      Level 1: Very Easy (syntax, basic definitions, direct application)
      Level 2: Easy (fundamental logic, basic loops/conditions, single concept)
      Level 3: Medium (intermediate algorithms, multiple interacting concepts, interview standards)
      Level 4: Hard (optimization, edge cases, advanced data structures, algorithm design)
      Level 5: Very Hard (advanced DP, graph theory, multi-step insight, tight constraints)
      Level 6: Expert (exceptional architecture, complex system design, novel trade-offs)
    """

    LEVEL_TO_NAME = {
        1: "very_easy",
        2: "easy",
        3: "medium",
        4: "hard",
        5: "very_hard",
        6: "expert",
    }

    NAME_TO_LEVEL = {
        "very_easy": 1,
        "easy": 2,
        "medium": 3,
        "hard": 4,
        "very_hard": 5,
        "expert": 6,
    }

    # Strict prerequisite score ceilings for 0-10 mastery evaluation
    TIER_SCORE_CEILINGS = {
        0: 0.0,
        1: 3.5,  # Level 1 only: cannot exceed 3.5 / 10
        2: 4.5,  # Level 2 only: cannot exceed 4.5 / 10
        3: 6.5,  # Level 3: cannot exceed 6.5 / 10
        4: 8.0,  # Level 4: cannot exceed 8.0 / 10
        5: 9.0,  # Level 5: cannot exceed 9.0 / 10
        6: 10.0, # Level 6: required to unlock 9.1 - 10.0 / 10
    }

    @staticmethod
    def get_difficulty_level_from_str(diff_str: str) -> int:
        norm = (diff_str or "").lower().strip()
        return AdaptiveEngine.NAME_TO_LEVEL.get(norm, 2)

    @staticmethod
    def get_difficulty_str_from_level(level: int) -> str:
        clamped = max(1, min(6, level))
        return AdaptiveEngine.LEVEL_TO_NAME.get(clamped, "easy")

    @classmethod
    def get_adaptive_next_difficulty_level(
        cls,
        attempts: List[AssessmentAttempt],
        initial_baseline_level: int = 2,
    ) -> int:
        """
        Calculates the target difficulty level (1-6) for the next question
        using dynamic consecutive performance progression.
        """
        if not attempts:
            return max(1, min(6, initial_baseline_level))

        # Sort attempts chronologically
        from datetime import datetime, timezone
        min_date = datetime.min.replace(tzinfo=timezone.utc)
        sorted_attempts = sorted(attempts, key=lambda a: a.created_at if a.created_at else min_date)
        last_attempt = sorted_attempts[-1]
        last_q = last_attempt.question
        current_level = last_q.difficulty_level if last_q else cls.get_difficulty_level_from_str(last_q.difficulty if last_q else "easy")

        # 1. Check last 2 attempts for consistent trend
        recent = sorted_attempts[-2:]
        if len(recent) >= 2:
            all_correct = all(
                (a.is_correct is True or a.score >= 70.0) for a in recent
            )
            all_failed = all(
                (a.is_correct is False or a.score < 40.0) for a in recent
            )

            if all_correct:
                # 2 consecutive successes: Promote by 1 tier
                return min(6, current_level + 1)
            elif all_failed:
                # 2 consecutive failures: Demote by 1 tier to stabilize capability floor
                return max(1, current_level - 1)

        # 2. Single attempt decisive trigger (e.g. perfect 100% on a hard coding problem or 0% complete failure)
        if len(recent) == 1:
            if last_attempt.score >= 90.0 and current_level < 6:
                return min(6, current_level + 1)
            elif last_attempt.score <= 20.0 and current_level > 1:
                return max(1, current_level - 1)

        # 3. Otherwise remain at current level to gather more discriminative evidence
        return max(1, min(6, current_level))

    @classmethod
    def estimate_user_ability(cls, attempts: List[AssessmentAttempt]) -> Dict[str, Any]:
        """
        Item Response Theory (IRT) inspired ability estimation:
        Returns:
          - ability_theta: estimated continuous ability in [1.0, 6.0]
          - highest_tier_passed: highest level where score >= 60%
          - highest_tier_attempted: highest level question seen
          - confidence: confidence metric in [0.0, 1.0]
          - subtopic_abilities: breakdown by subtopic/category
        """
        if not attempts:
            return {
                "ability_theta": 2.0,
                "highest_tier_passed": 0,
                "highest_tier_attempted": 0,
                "confidence": 0.0,
                "passed_count": 0,
                "total_count": 0,
                "subtopic_abilities": {},
            }

        total = len(attempts)
        passed_attempts = [a for a in attempts if (a.is_correct is True or a.score >= 60.0)]
        
        highest_attempted = 0
        highest_passed = 0
        
        weighted_level_sum = 0.0
        weighted_denom = 0.0
        subtopics: Dict[str, List[float]] = {}

        for a in attempts:
            q = a.question
            level = (q.difficulty_level if q and q.difficulty_level else cls.get_difficulty_level_from_str(q.difficulty if q else "easy"))
            highest_attempted = max(highest_attempted, level)
            
            score_ratio = max(0.0, min(1.0, a.score / 100.0))
            if score_ratio >= 0.6:
                highest_passed = max(highest_passed, level)

            weight = float(level)
            weighted_level_sum += weight * score_ratio * level
            weighted_denom += weight * max(0.2, score_ratio)

            # Subtopic tracking
            sub = (q.subtopic if q and q.subtopic else (q.category if q else "general"))
            subtopics.setdefault(sub, []).append(a.score)

        if weighted_denom > 0:
            raw_theta = weighted_level_sum / weighted_denom
            theta = max(1.0, min(6.0, raw_theta))
        else:
            theta = 1.0

        # Confidence increases with number of questions up to 10
        confidence = min(1.0, total / 10.0)

        # Average score per subtopic
        subtopic_breakdown = {
            k: round(sum(v) / len(v), 1) for k, v in subtopics.items()
        }

        return {
            "ability_theta": round(theta, 2),
            "highest_tier_passed": highest_passed,
            "highest_tier_attempted": highest_attempted,
            "confidence": round(confidence, 2),
            "passed_count": len(passed_attempts),
            "total_count": total,
            "subtopic_abilities": subtopic_breakdown,
        }

    @classmethod
    def calculate_calibrated_mastery_score(
        cls,
        attempts: List[AssessmentAttempt],
    ) -> Dict[str, Any]:
        """
        Calibrated 0 to 10 mastery evaluation based on difficulty weighting
        and strict prerequisite ceilings.
        
        A user answering only Level 1-2 questions correctly cannot exceed 4.5/10.
        A score of 9.5-10.0 strictly requires passing Level 6 (Expert) challenges.
        """
        if not attempts:
            return {
                "mastery_score": 0.0,
                "mastery_band": "Novice",
                "highest_tier_passed": "None",
                "highest_tier_level": 0,
                "ceiling_applied": 0.0,
                "average_score": 0.0,
            }

        total = len(attempts)
        ability_info = cls.estimate_user_ability(attempts)
        highest_passed_lvl = ability_info["highest_tier_passed"]

        # 1. Compute difficulty-weighted score
        weighted_points = 0.0
        total_weight = 0.0
        simple_score_sum = 0.0

        for a in attempts:
            q = a.question
            level = (q.difficulty_level if q and q.difficulty_level else cls.get_difficulty_level_from_str(q.difficulty if q else "easy"))
            weight = float(level)
            
            score_ratio = max(0.0, min(1.0, a.score / 100.0))
            weighted_points += weight * score_ratio
            total_weight += weight
            simple_score_sum += a.score

        avg_score = simple_score_sum / total if total > 0 else 0.0

        if total_weight > 0:
            normalized_performance = weighted_points / total_weight
        else:
            normalized_performance = 0.0

        # Base 0-10 calculation: performance scaled by highest difficulty ratio
        tier_scale_factor = (highest_passed_lvl / 6.0) ** 0.5 if highest_passed_lvl > 0 else 0.2
        raw_mastery = 10.0 * normalized_performance * tier_scale_factor

        # 2. Enforce strict prerequisite ceiling
        ceiling = cls.TIER_SCORE_CEILINGS.get(highest_passed_lvl, 3.5)
        calibrated_score = round(min(raw_mastery, ceiling), 1)

        # 3. Determine calibrated mastery band
        if calibrated_score >= 9.0:
            band = "Master / Principal"
        elif calibrated_score >= 8.0:
            band = "Advanced Specialist"
        elif calibrated_score >= 6.5:
            band = "Proficient Engineer"
        elif calibrated_score >= 4.5:
            band = "Competent Practitioner"
        elif calibrated_score >= 3.0:
            band = "Advanced Beginner"
        else:
            band = "Novice"

        return {
            "mastery_score": calibrated_score,
            "mastery_band": band,
            "highest_tier_passed": cls.LEVEL_TO_NAME.get(highest_passed_lvl, "None"),
            "highest_tier_level": highest_passed_lvl,
            "ceiling_applied": ceiling,
            "average_score": round(avg_score, 1),
            "estimated_ability": ability_info["ability_theta"],
            "subtopic_abilities": ability_info["subtopic_abilities"],
        }

    @staticmethod
    def get_semantic_title_root(title: str) -> str:
        """Extracts semantic base title stripped of case numbers, patterns, and levels."""
        if not title:
            return ""
        t = re.sub(r"^###\s*", "", title)
        t = re.sub(r"\(Level\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Case\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Topic\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Pattern\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Scenario\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Depth\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Analysis\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\(Concept Focus\s+\d+[^)]*\)", "", t, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", t).strip().lower()

    @staticmethod
    def extract_prompt_tokens(prompt: str) -> Set[str]:
        """Extracts normalized significant word tokens from a prompt."""
        if not prompt:
            return set()
        clean = re.sub(r"```[\s\S]*?```", " ", prompt)  # exclude code blocks from text tokens
        clean = re.sub(r"[^\w\s]", " ", clean.lower())
        return {w for w in clean.split() if len(w) > 3}

    @staticmethod
    def extract_code_signature(q: Question) -> str:
        """Extracts normalized code snippet from question evaluation metadata or prompt."""
        meta = q.evaluation_metadata or {}
        code = meta.get("code") or meta.get("buggy_code") or meta.get("starter_code") or ""
        if not code and "```" in (q.prompt or ""):
            m = re.search(r"```(?:\w+)?\n([\s\S]*?)```", q.prompt or "")
            if m:
                code = m.group(1)
        # Normalize whitespace
        return re.sub(r"\s+", "", code).strip()

    @classmethod
    def get_next_question(
        cls,
        assessment: Assessment,
        db: Session,
        max_questions: int = 10,
    ) -> Optional[Question]:
        """
        Dynamically selects the next best adaptive question matching the candidate's
        target difficulty level with randomized rotation and semantic deduplication.
        
        Guarantees:
          - Never repeat the same question ID in one assessment.
          - Never show semantically identical questions under different IDs.
          - Exclude previously answered and already presented questions.
          - Randomize selection among eligible candidates (no static .first()).
          - If the question pool is exhausted, return None gracefully (never repeat!).
        """
        # Fetch attempts from both DB and any in-memory session objects
        db_attempts = (
            db.query(AssessmentAttempt)
            .filter(AssessmentAttempt.assessment_id == assessment.id)
            .all()
        )
        seen_map = {}
        for a in list(assessment.attempts or []) + db_attempts:
            key = a.id if a.id else id(a)
            seen_map[key] = a
        fresh_attempts = list(seen_map.values())

        if len(fresh_attempts) >= max_questions:
            return None

        attempted_q_ids = [a.question_id for a in fresh_attempts if a.question_id]
        
        # Build semantic seen records from attempted questions
        seen_title_roots: Set[str] = set()
        seen_token_sets: List[Set[str]] = []
        seen_code_signatures: Set[str] = set()

        if attempted_q_ids:
            attempted_questions = db.query(Question).filter(Question.id.in_(attempted_q_ids)).all()
            for aq in attempted_questions:
                t_root = cls.get_semantic_title_root(aq.title or "")
                if t_root:
                    seen_title_roots.add(t_root)
                tokens = cls.extract_prompt_tokens(aq.prompt or "")
                if tokens:
                    seen_token_sets.append(tokens)
                code_sig = cls.extract_code_signature(aq)
                if code_sig and len(code_sig) > 20:
                    seen_code_signatures.add(code_sig)

        def is_semantic_duplicate(candidate: Question) -> bool:
            """Check if candidate matches any previously attempted question in this assessment."""
            # 1. Exact ID
            if candidate.id in attempted_q_ids:
                return True

            # 2. Semantic title root match
            cand_root = cls.get_semantic_title_root(candidate.title or "")
            if cand_root and cand_root in seen_title_roots:
                return True

            # 3. Exact code signature match
            cand_code_sig = cls.extract_code_signature(candidate)
            if cand_code_sig and len(cand_code_sig) > 20 and cand_code_sig in seen_code_signatures:
                return True

            # 4. Token overlap (Jaccard similarity >= 0.70 with at least 3 matching significant words)
            cand_tokens = cls.extract_prompt_tokens(candidate.prompt or "")
            if cand_tokens and len(cand_tokens) >= 3:
                for seen_tokens in seen_token_sets:
                    if len(seen_tokens) >= 3:
                        intersection = cand_tokens.intersection(seen_tokens)
                        union = cand_tokens.union(seen_tokens)
                        if len(intersection) >= 3 and union:
                            sim = len(intersection) / len(union)
                            if sim >= 0.70:
                                return True

            return False

        # Calculate next target difficulty level (1-6)
        target_lvl = cls.get_adaptive_next_difficulty_level(fresh_attempts)

        topics = assessment.selected_topics or []
        base_query = db.query(Question).join(AssessmentTopic).filter(
            Question.is_active.is_(True),
            Question.validation_status == "validated",
            ~Question.id.in_(attempted_q_ids) if attempted_q_ids else True,
        )
        if topics:
            base_query = base_query.filter(AssessmentTopic.name.in_(topics))

        # Filter by assessment mode
        if assessment.mode == "coding":
            base_query = base_query.filter(Question.question_type == "coding")
        elif assessment.mode == "sql":
            base_query = base_query.filter(Question.question_type == "sql")
        elif assessment.mode == "quiz":
            base_query = base_query.filter(
                Question.question_type.in_(["multiple_choice", "output_prediction", "debugging", "conceptual"])
            )

        def pick_candidate_from_query(query) -> Optional[Question]:
            """Retrieve candidates randomly and return the first non-duplicate."""
            candidates = query.order_by(func.random()).limit(30).all()
            for cand in candidates:
                if not is_semantic_duplicate(cand):
                    return cand
            return None

        # 1. Try exact target difficulty level
        target_name = cls.get_difficulty_str_from_level(target_lvl)
        q = pick_candidate_from_query(
            base_query.filter(
                (Question.difficulty_level == target_lvl) | (Question.difficulty == target_name)
            )
        )

        # 2. Adjacent level fallback (target - 1, then target + 1, etc.)
        if not q:
            adjacent_levels = [target_lvl - 1, target_lvl + 1, target_lvl - 2, target_lvl + 2, target_lvl - 3, target_lvl + 3]
            for adj in adjacent_levels:
                if 1 <= adj <= 6:
                    adj_name = cls.get_difficulty_str_from_level(adj)
                    q = pick_candidate_from_query(
                        base_query.filter(
                            (Question.difficulty_level == adj) | (Question.difficulty == adj_name)
                        )
                    )
                    if q:
                        break

        # 3. Fallback to any remaining difficulty within selected topics & mode
        if not q:
            q = pick_candidate_from_query(base_query)

        # 4. Fallback to related questions in same skill if selected topics exhausted
        if not q and topics:
            skill_query = db.query(Question).filter(
                Question.is_active.is_(True),
                Question.validation_status == "validated",
                ~Question.id.in_(attempted_q_ids) if attempted_q_ids else True,
            )
            if assessment.mode == "coding":
                skill_query = skill_query.filter(Question.question_type == "coding")
            elif assessment.mode == "sql":
                skill_query = skill_query.filter(Question.question_type == "sql")
            elif assessment.mode == "quiz":
                skill_query = skill_query.filter(
                    Question.question_type.in_(["multiple_choice", "output_prediction", "debugging", "conceptual"])
                )
            q = pick_candidate_from_query(skill_query)

        # If pool is truly exhausted, return None gracefully (NEVER repeat a question)
        return q


adaptive_engine = AdaptiveEngine()
