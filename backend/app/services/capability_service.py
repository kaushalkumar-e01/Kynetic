from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.skill import EvidenceRecord, UserCapability


def recalculate_user_capability(user_id: str, skill_id: str, db: Session) -> UserCapability:
    """
    Evidence-based proficiency and confidence calculation for a user skill.
    """
    db.flush()
    evidence_records = (
        db.query(EvidenceRecord)
        .filter(EvidenceRecord.user_id == user_id, EvidenceRecord.skill_id == skill_id)
        .all()
    )

    if not evidence_records:
        capability = (
            db.query(UserCapability)
            .filter(UserCapability.user_id == user_id, UserCapability.skill_id == skill_id)
            .first()
        )
        if not capability:
            capability = UserCapability(
                user_id=user_id,
                skill_id=skill_id,
                estimated_band="unverified",
                score=0.0,
                confidence=0.0,
                evidence_count=0,
                last_evaluated_at=datetime.now(timezone.utc),
            )
            db.add(capability)
            db.flush()
        else:
            capability.score = 0.0
            capability.confidence = 0.0
            capability.estimated_band = "unverified"
            capability.evidence_count = 0
            capability.last_evaluated_at = datetime.now(timezone.utc)
            db.flush()
        return capability

    has_claims = False
    claim_count = 0

    # Group assessments by unique question id (source_record_id) to avoid duplicate score inflation
    assessments_by_question: Dict[str, Dict[str, Any]] = {}

    # Group projects by unique project id (source_record_id)
    projects_by_id: Dict[str, Dict[str, Any]] = {}

    for ev in evidence_records:
        stype = (ev.source_type or "").lower().strip()
        meta = ev.quality_metadata or {}

        if stype in ["resume", "user-confirmed", "profile", "claimed"]:
            has_claims = True
            claim_count += 1

        elif stype == "assessment":
            q_id = str(ev.source_record_id or ev.id)
            score_val = float(meta.get("score", 100.0 if meta.get("is_correct", True) else 0.0))
            difficulty = str(meta.get("difficulty", "medium")).lower()

            # Keep best attempt for this unique question
            if q_id not in assessments_by_question or score_val > assessments_by_question[q_id]["score"]:
                assessments_by_question[q_id] = {
                    "score": score_val,
                    "difficulty": difficulty,
                    "is_correct": meta.get("is_correct", score_val >= 60.0),
                }

        elif stype == "project":
            p_id = str(ev.source_record_id or ev.id)
            is_code_verified = bool(meta.get("code_verified", False))
            if p_id not in projects_by_id or (is_code_verified and not projects_by_id[p_id]["code_verified"]):
                projects_by_id[p_id] = {
                    "code_verified": is_code_verified,
                }

    # Calculate assessment points (max 75 pts)
    easy_points = 0.0
    medium_points = 0.0
    hard_points = 0.0
    assessment_conf_sum = 0.0

    for q_data in assessments_by_question.values():
        ratio = max(0.0, min(1.0, q_data["score"] / 100.0))
        diff = q_data["difficulty"]

        if diff == "easy":
            easy_points += 10.0 * ratio
        elif diff == "hard":
            hard_points += 20.0 * ratio
        else:  # default medium
            medium_points += 15.0 * ratio

        assessment_conf_sum += 0.12 if q_data["is_correct"] else 0.05

    # Cap by difficulty tier
    easy_points = min(20.0, easy_points)
    medium_points = min(30.0, medium_points)
    hard_points = min(30.0, hard_points)
    total_assessment_points = min(75.0, easy_points + medium_points + hard_points)

    # Calculate project points (max 25 pts)
    project_points = 0.0
    project_conf_sum = 0.0
    for p_data in projects_by_id.values():
        if p_data["code_verified"]:
            project_points += 15.0
            project_conf_sum += 0.20
        else:
            project_points += 5.0
            project_conf_sum += 0.08

    project_points = min(25.0, project_points)

    # Verified proficiency score (claims contribute 0.0 points!)
    total_score = round(min(100.0, total_assessment_points + project_points), 1)

    # Calculate confidence (0.0 to 0.98)
    base_claim_conf = min(0.20, 0.10 + (0.05 * min(claim_count, 2))) if has_claims else 0.0
    total_conf = round(min(0.98, base_claim_conf + assessment_conf_sum + project_conf_sum), 2)

    # Assign estimated band
    if total_score >= 80.0:
        estimated_band = "advanced"
    elif total_score >= 50.0:
        estimated_band = "proficient"
    elif total_score > 0.0:
        estimated_band = "foundational"
    elif has_claims:
        estimated_band = "claimed"
    else:
        estimated_band = "unverified"

    # Update or create UserCapability
    capability = (
        db.query(UserCapability)
        .filter(UserCapability.user_id == user_id, UserCapability.skill_id == skill_id)
        .first()
    )
    if not capability:
        capability = UserCapability(
            user_id=user_id,
            skill_id=skill_id,
            estimated_band=estimated_band,
            score=total_score,
            confidence=total_conf,
            evidence_count=len(evidence_records),
            last_evaluated_at=datetime.now(timezone.utc),
        )
        db.add(capability)
    else:
        capability.score = total_score
        capability.confidence = total_conf
        capability.estimated_band = estimated_band
        capability.evidence_count = len(evidence_records)
        capability.last_evaluated_at = datetime.now(timezone.utc)

    db.flush()
    return capability


def recalculate_all_capabilities_for_user(user_id: str, db: Session) -> List[UserCapability]:
    """Recalculates all skills for a given user according to principled scoring."""
    skill_ids = [
        row[0]
        for row in db.query(EvidenceRecord.skill_id)
        .filter(EvidenceRecord.user_id == user_id)
        .distinct()
        .all()
    ]
    # Also check if user has capabilities without evidence
    cap_skill_ids = [
        row[0]
        for row in db.query(UserCapability.skill_id)
        .filter(UserCapability.user_id == user_id)
        .distinct()
        .all()
    ]
    all_skill_ids = set(skill_ids + cap_skill_ids)

    updated = []
    for sid in all_skill_ids:
        cap = recalculate_user_capability(user_id, sid, db)
        updated.append(cap)
    return updated

