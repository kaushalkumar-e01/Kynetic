from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.skill import Skill, EvidenceRecord, UserCapability
from app.models.activity import UserActivity
from app.services.capability_service import recalculate_user_capability
from app.schemas.skill import (
    SkillResponse,
    EvidenceRecordResponse,
    UserCapabilityResponse,
    CreateEvidenceRequest,
)

router = APIRouter()


@router.get(
    "/skills",
    response_model=List[SkillResponse],
    summary="List available canonical skills",
)
def list_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).order_by(Skill.canonical_name).all()
    return [SkillResponse.model_validate(s) for s in skills]


@router.get(
    "/capabilities",
    response_model=List[UserCapabilityResponse],
    summary="List authenticated user's skill capabilities",
)
def list_user_capabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    capabilities = (
        db.query(UserCapability)
        .filter(UserCapability.user_id == current_user.id)
        .order_by(desc(UserCapability.score))
        .all()
    )
    results = []
    for c in capabilities:
        cap_dto = UserCapabilityResponse.model_validate(c)
        if c.skill:
            cap_dto.skill_name = c.skill.canonical_name
            cap_dto.category = c.skill.category
        cap_dto.mastery_score = round(c.score / 10.0, 1)
        results.append(cap_dto)
    return results


@router.get(
    "/capabilities/{skill_id}",
    response_model=UserCapabilityResponse,
    summary="Get user capability for a specific skill",
)
def get_user_capability(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    capability = (
        db.query(UserCapability)
        .filter(UserCapability.user_id == current_user.id, UserCapability.skill_id == skill_id)
        .first()
    )
    if not capability:
        raise NotFoundException("Capability for this skill not found.")

    cap_dto = UserCapabilityResponse.model_validate(capability)
    if capability.skill:
        cap_dto.skill_name = capability.skill.canonical_name
        cap_dto.category = capability.skill.category
    cap_dto.mastery_score = round(capability.score / 10.0, 1)
    return cap_dto


@router.get(
    "/evidence",
    response_model=List[EvidenceRecordResponse],
    summary="List authenticated user's evidence records",
)
def list_user_evidence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(EvidenceRecord)
        .filter(EvidenceRecord.user_id == current_user.id)
        .order_by(desc(EvidenceRecord.observed_at))
        .all()
    )
    return [EvidenceRecordResponse.model_validate(r) for r in records]


@router.post(
    "/evidence",
    response_model=EvidenceRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add user-confirmed skill evidence",
)
def add_user_evidence(
    payload: CreateEvidenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    canonical_name = payload.skill_name.strip().title()
    skill = db.query(Skill).filter(Skill.canonical_name == canonical_name).first()
    if not skill:
        skill = Skill(canonical_name=canonical_name, category=payload.category)
        db.add(skill)
        db.flush()

    evidence = EvidenceRecord(
        user_id=current_user.id,
        skill_id=skill.id,
        source_type="user-confirmed",
        summary=payload.summary,
        confidence=payload.confidence,
        quality_metadata={"user_reported": True},
    )
    db.add(evidence)

    # Recalculate capability based on evidence (claims start at score 0.0)
    recalculate_user_capability(user_id=current_user.id, skill_id=skill.id, db=db)

    activity = UserActivity(
        user_id=current_user.id,
        activity_type="evidence_added",
        related_record_type="evidence",
        details={"skill": canonical_name},
    )
    db.add(activity)

    db.commit()
    db.refresh(evidence)
    return EvidenceRecordResponse.model_validate(evidence)

