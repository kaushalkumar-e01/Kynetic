from app.models.user import User
from app.models.assistant import AssistantConversation
from app.models.skill import Skill, UserCapability
from app.core.security import get_password_hash
from app.schemas.assistant import SendMessageRequest
from app.api.v1.endpoints.assistant import (
    send_assistant_message,
    list_conversations,
    get_conversation,
    delete_conversation,
)


def test_assistant_chat_and_context_awareness(db_session):
    user = User(email="assistant_tester@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    # Pre-populate user skill
    skill = Skill(canonical_name="Python", category="language")
    db_session.add(skill)
    db_session.flush()

    cap = UserCapability(user_id=user.id, skill_id=skill.id, score=85.0, estimated_band="proficient", confidence=0.85)
    db_session.add(cap)
    db_session.commit()
    db_session.refresh(user)

    # 1. Send initial message asking about skill gaps
    req = SendMessageRequest(message="What are my current capabilities and skill gaps?")
    conv_dto = send_assistant_message(payload=req, current_user=user, db=db_session)

    assert conv_dto.id is not None
    assert len(conv_dto.messages) == 2  # 1 user + 1 assistant
    assert conv_dto.messages[0].role == "user"
    assert conv_dto.messages[1].role == "assistant"
    # Assistant response should reference user's tracked skill
    assert "Python" in conv_dto.messages[1].content

    # 2. Continue conversation
    req2 = SendMessageRequest(message="How should I prepare for a backend interview?", conversation_id=conv_dto.id)
    conv_dto2 = send_assistant_message(payload=req2, current_user=user, db=db_session)
    assert conv_dto2.id == conv_dto.id
    assert len(conv_dto2.messages) == 4

    # 3. List conversations
    conv_list = list_conversations(current_user=user, db=db_session)
    assert len(conv_list) == 1
    assert conv_list[0].id == conv_dto.id
    assert conv_list[0].message_count == 4

    # 4. Get conversation details
    detail = get_conversation(conversation_id=conv_dto.id, current_user=user, db=db_session)
    assert len(detail.messages) == 4

    # 5. Delete conversation
    del_res = delete_conversation(conversation_id=conv_dto.id, current_user=user, db=db_session)
    assert "deleted successfully" in del_res["message"]
    assert db_session.query(AssistantConversation).filter_by(id=conv_dto.id).first() is None


def test_assistant_multi_user_isolation(db_session):
    user_a = User(email="user_a_chat@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    user_b = User(email="user_b_chat@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add_all([user_a, user_b])
    db_session.commit()
    db_session.refresh(user_a)
    db_session.refresh(user_b)

    # User A creates a conversation
    req = SendMessageRequest(message="Alice's confidential message")
    conv_a = send_assistant_message(payload=req, current_user=user_a, db=db_session)

    # User B lists conversations -> must be 0
    b_convs = list_conversations(current_user=user_b, db=db_session)
    assert len(b_convs) == 0

    # User B tries to access User A's conversation -> raises NotFoundException
    import pytest
    from app.core.errors import NotFoundException

    with pytest.raises(NotFoundException):
        get_conversation(conversation_id=conv_a.id, current_user=user_b, db=db_session)

