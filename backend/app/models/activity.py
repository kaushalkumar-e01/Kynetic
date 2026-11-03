from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserActivity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_activities"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    activity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # e.g., resume_uploaded, quiz_completed, project_analyzed
    related_record_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_record_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="activities")
