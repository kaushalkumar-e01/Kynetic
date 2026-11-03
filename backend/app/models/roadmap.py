from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.goal import Goal


class Roadmap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roadmaps"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    goal_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, completed, paused

    user: Mapped["User"] = relationship("User", back_populates="roadmaps")
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="roadmaps")
    milestones: Mapped[List["RoadmapMilestone"]] = relationship("RoadmapMilestone", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapMilestone.ordering")


class RoadmapMilestone(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roadmap_milestones"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    roadmap_id: Mapped[str] = mapped_column(String(36), ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resources: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    ordering: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, in_progress, completed
    due_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="milestones")
