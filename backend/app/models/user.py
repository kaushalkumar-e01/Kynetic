from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.project import Project, ConnectedAccount
    from app.models.assessment import Assessment, AssessmentAttempt
    from app.models.skill import EvidenceRecord, UserCapability
    from app.models.goal import Goal, JobMatch
    from app.models.roadmap import Roadmap
    from app.models.activity import UserActivity
    from app.models.assistant import AssistantConversation


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    account_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes: Mapped[List["Resume"]] = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    connected_accounts: Mapped[List["ConnectedAccount"]] = relationship("ConnectedAccount", back_populates="user", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    assessment_attempts: Mapped[List["AssessmentAttempt"]] = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    evidence_records: Mapped[List["EvidenceRecord"]] = relationship("EvidenceRecord", back_populates="user", cascade="all, delete-orphan")
    user_capabilities: Mapped[List["UserCapability"]] = relationship("UserCapability", back_populates="user", cascade="all, delete-orphan")
    goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    job_matches: Mapped[List["JobMatch"]] = relationship("JobMatch", back_populates="user", cascade="all, delete-orphan")
    roadmaps: Mapped[List["Roadmap"]] = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    activities: Mapped[List["UserActivity"]] = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    conversations: Mapped[List["AssistantConversation"]] = relationship("AssistantConversation", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    education_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    experience_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_domains: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    learning_preferences: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")
