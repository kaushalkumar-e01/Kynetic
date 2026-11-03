from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, JSON, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class AssessmentTopic(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessment_topics"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    parent_topic_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("assessment_topics.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    questions: Mapped[List["Question"]] = relationship("Question", back_populates="topic", cascade="all, delete-orphan")


class Question(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "questions"

    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessment_topics.id", ondelete="CASCADE"), index=True, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # multiple_choice, multi_select, output_prediction, debugging, coding
    difficulty: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # easy, medium, hard
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)  # List of choices for MCQ
    evaluation_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Hidden answers/test cases
    source_attribution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped["AssessmentTopic"] = relationship("AssessmentTopic", back_populates="questions")
    attempts: Mapped[List["AssessmentAttempt"]] = relationship("AssessmentAttempt", back_populates="question", cascade="all, delete-orphan")


class Assessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessments"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(50), default="assessment", nullable=False)  # practice, assessment
    selected_topics: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    summary_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="assessments")
    attempts: Mapped[List["AssessmentAttempt"]] = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentAttempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assessment_attempts"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    submitted_answer: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    execution_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Sandboxed execution details
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="assessment_attempts")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="attempts")
    question: Mapped["Question"] = relationship("Question", back_populates="attempts")
