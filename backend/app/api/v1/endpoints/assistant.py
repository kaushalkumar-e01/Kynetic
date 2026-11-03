from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.assistant import AssistantConversation
from app.schemas.assistant import (
    SendMessageRequest,
    MessageResponse,
    ConversationResponse,
    ConversationSummaryResponse,
)
from app.services.assistant_service import assistant_service

router = APIRouter()


@router.post(
    "/messages",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI assistant with workspace context",
)
def send_assistant_message(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = assistant_service.send_message(
        user_id=current_user.id,
        message_text=payload.message,
        conversation_id=payload.conversation_id,
        db=db,
    )
    dto = ConversationResponse.model_validate(conv)
    dto.messages = [MessageResponse.model_validate(m) for m in conv.messages]
    return dto


@router.get(
    "/conversations",
    response_model=List[ConversationSummaryResponse],
    summary="List authenticated user's conversations",
)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = (
        db.query(AssistantConversation)
        .filter(AssistantConversation.user_id == current_user.id)
        .order_by(desc(AssistantConversation.updated_at))
        .all()
    )
    results = []
    for c in conversations:
        results.append(
            ConversationSummaryResponse(
                id=c.id,
                title=c.title,
                message_count=len(c.messages),
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return results


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation history with all messages",
)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(AssistantConversation).filter_by(id=conversation_id, user_id=current_user.id).first()
    if not conv:
        raise NotFoundException("Conversation not found or access denied.")

    dto = ConversationResponse.model_validate(conv)
    dto.messages = [MessageResponse.model_validate(m) for m in conv.messages]
    return dto


@router.delete(
    "/conversations/{conversation_id}",
    summary="Delete a conversation and its messages",
)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = db.query(AssistantConversation).filter_by(id=conversation_id, user_id=current_user.id).first()
    if not conv:
        raise NotFoundException("Conversation not found or access denied.")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully."}

