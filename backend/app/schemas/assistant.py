from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's query or instruction for the AI assistant")
    conversation_id: Optional[str] = Field(None, description="Optional existing conversation ID to continue")


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationSummaryResponse(BaseModel):
    id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

