from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.roadmap import Roadmap


class Goal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "goals"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    goal_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # placement, career, project, learning
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, completed, archived

    user: Mapped["User"] = relationship("User", back_populates="goals")
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="goal", cascade="all, delete-orphan")
    roadmaps: Mapped[list["Roadmap"]] = relationship("Roadmap", back_populates="goal", cascade="all, delete-orphan")


class JobMatch(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_matches"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    goal_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    job_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extracted_requirements: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    match_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    estimated_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    limitations: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="job_matches")
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="job_matches")
