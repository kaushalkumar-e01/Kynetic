from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, ForeignKey, JSON, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Skill(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "skills"

    canonical_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # e.g., language, framework, database, concept
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evidence_records: Mapped[List["EvidenceRecord"]] = relationship("EvidenceRecord", back_populates="skill", cascade="all, delete-orphan")
    capabilities: Mapped[List["UserCapability"]] = relationship("UserCapability", back_populates="skill", cascade="all, delete-orphan")


class EvidenceRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "evidence_records"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # resume, assessment, project, profile, user-confirmed
    source_record_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    quality_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="evidence_records")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="evidence_records")


class UserCapability(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_capabilities"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill_capability"),)

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    estimated_band: Mapped[str] = mapped_column(String(50), default="unverified", nullable=False)  # unverified, claimed, foundational, proficient, advanced
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_capabilities")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="capabilities")
