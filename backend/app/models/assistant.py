from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class AssistantConversation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assistant_conversations"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation", nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["AssistantMessage"]] = relationship(
        "AssistantMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AssistantMessage.created_at",
    )


class AssistantMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "assistant_messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("assistant_conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    conversation: Mapped["AssistantConversation"] = relationship("AssistantConversation", back_populates="messages")
