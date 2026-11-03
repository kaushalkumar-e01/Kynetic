from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    file_storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    version_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="resumes")
    analyses: Mapped[List["ResumeAnalysis"]] = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")


class ResumeAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "resume_analyses"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[str] = mapped_column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    extracted_profile: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    strengths: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    suggestions: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    model_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="analyses")
