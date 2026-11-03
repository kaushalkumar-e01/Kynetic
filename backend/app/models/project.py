from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, JSON, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)  # manual, github
    repository_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    access_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    analyses: Mapped[List["ProjectAnalysis"]] = relationship("ProjectAnalysis", back_populates="project", cascade="all, delete-orphan")


class ProjectAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "project_analyses"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_technologies: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    architecture_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    demonstrated_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    missing_requirements: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    source_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="analyses")


class ConnectedAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "connected_accounts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # github, linkedin
    provider_account_id: Mapped[str] = mapped_column(String(128), nullable=False)
    encrypted_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Encrypted at rest
    granted_scopes: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    disconnected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="connected_accounts")
