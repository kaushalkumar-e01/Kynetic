import time
from app.models.user import User, UserProfile
from app.models.skill import Skill, UserCapability
from app.models.project import Project
from app.core.security import get_password_hash
from app.schemas.assistant import SendMessageRequest
from app.api.v1.endpoints.assistant import send_assistant_message
from app.services.assistant_router import classify_query, QueryType


def test_type_a_casual_fast_path(db_session):
    user = User(email="casual_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Greeting
    start_t = time.time()
    req = SendMessageRequest(message="Hi!")
    conv = send_assistant_message(payload=req, current_user=user, db=db_session)
    elapsed = time.time() - start_t

    # Response should be virtually instant (under 0.2s even with DB message insert)
    assert elapsed < 0.5
    assert len(conv.messages) == 2
    reply = conv.messages[1].content
    assert any(g in reply.lower() for g in ["hey", "hello", "great to see you"])

    # 2. Thank you
    req2 = SendMessageRequest(message="Thanks so much!", conversation_id=conv.id)
    conv2 = send_assistant_message(payload=req2, current_user=user, db=db_session)
    assert len(conv2.messages) == 4
    reply2 = conv2.messages[3].content
    assert any(w in reply2.lower() for w in ["welcome", "let me know", "glad"])


def test_type_b_general_knowledge(db_session):
    user = User(email="gk_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # General question about Python without personal context
    req = SendMessageRequest(message="What is Python?")
    conv = send_assistant_message(payload=req, current_user=user, db=db_session)

    assert len(conv.messages) == 2
    reply = conv.messages[1].content
    assert "Python" in reply or "programming" in reply.lower()
    # Should not apologize for missing candidate workspace data
    assert "you currently have no" not in reply.lower()


def test_type_c_workspace_specific_selective_retrieval(db_session):
    user = User(email="workspace_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill = Skill(canonical_name="FastAPI", category="framework")
    db_session.add(skill)
    db_session.flush()

    cap = UserCapability(user_id=user.id, skill_id=skill.id, score=90.0, estimated_band="proficient", confidence=0.9)
    db_session.add(cap)
    db_session.commit()
    db_session.refresh(user)

    # Asking specifically about skills
    decision = classify_query("What are my strongest skills?")
    assert decision.query_type == QueryType.WORKSPACE_SPECIFIC
    assert "skills" in decision.scope

    req = SendMessageRequest(message="What are my strongest skills?")
    conv = send_assistant_message(payload=req, current_user=user, db=db_session)
    assert len(conv.messages) == 2
    reply = conv.messages[1].content
    assert "FastAPI" in reply


def test_type_d_and_safety_fallback(db_session):
    user = User(email="complex_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.flush()

    skill = Skill(canonical_name="Docker", category="tool")
    db_session.add(skill)
    db_session.flush()

    cap = UserCapability(user_id=user.id, skill_id=skill.id, score=80.0, estimated_band="proficient", confidence=0.8)
    db_session.add(cap)
    db_session.commit()
    db_session.refresh(user)

    # 1. Complex analysis
    d1 = classify_query("Analyze my overall career readiness.")
    assert d1.query_type == QueryType.COMPLEX_ANALYSIS
    assert "all" in d1.scope

    # 2. Ambiguous query safety fallback (must NOT be treated as simple casual/general)
    d2 = classify_query("What should I do next?")
    assert d2.query_type == QueryType.COMPLEX_ANALYSIS
    assert "all" in d2.scope

    d3 = classify_query("Am I ready for backend development?")
    assert d3.query_type == QueryType.COMPLEX_ANALYSIS
    assert "all" in d3.scope

