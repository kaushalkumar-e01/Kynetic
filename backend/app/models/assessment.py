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
    category: Mapped[str] = mapped_column(String(100), default="cs_fundamentals", index=True, nullable=False)
    subtopic: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    question_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # multiple_choice, multi_select, output_prediction, debugging, coding, sql, conceptual
    difficulty: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # very_easy, easy, medium, hard, very_hard, expert
    difficulty_level: Mapped[int] = mapped_column(Integer, default=2, index=True, nullable=False)  # 1 to 6
    programming_language: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)  # c, cpp, java, python, javascript, sql, none
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)  # List of choices for MCQ
    evaluation_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # Hidden answers, test cases, rubrics
    source_attribution: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_name: Mapped[Optional[str]] = mapped_column(String(100), default="Kynetic Original Bank", nullable=True)
    source_license: Mapped[Optional[str]] = mapped_column(String(100), default="CC-BY-4.0", nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    validation_status: Mapped[str] = mapped_column(String(50), default="validated", index=True, nullable=False)  # draft, pending, validated, rejected, retired
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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
