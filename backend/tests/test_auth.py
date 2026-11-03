import pytest
from datetime import timedelta
from fastapi import Response
from starlette.requests import Request

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.errors import ConflictException, UnauthorizedException
from app.api.deps import get_current_user
from app.api.v1.endpoints.auth import register_user, login_user, logout_user
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.models.user import User
from app.models.activity import UserActivity


def test_password_hashing():
    password = "SuperSecretPassword123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_lifecycle():
    token = create_access_token(subject="user-12345")
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-12345"
    assert "exp" in decoded

    # Expired token test
    expired_token = create_access_token(subject="user-12345", expires_delta=timedelta(seconds=-10))
    decoded_expired = decode_access_token(expired_token)
    assert decoded_expired is None


def test_user_registration(db_session):
    payload = UserRegisterRequest(
        email="test_reg@example.com",
        password="ValidPassword123!",
        display_name="Test User",
    )
    response = Response()
    result = register_user(payload=payload, response=response, db=db_session)

    assert result.access_token is not None
    assert result.user.email == "test_reg@example.com"

    # Verify persistent records in database
    user_in_db = db_session.query(User).filter_by(email="test_reg@example.com").first()
    assert user_in_db is not None
    assert user_in_db.profile.display_name == "Test User"

    # Verify audit activity created
    activity = db_session.query(UserActivity).filter_by(user_id=user_in_db.id).first()
    assert activity is not None
    assert activity.activity_type == "account_registered"


def test_registration_duplicate_email_conflict(db_session):
    payload = UserRegisterRequest(
        email="duplicate@example.com",
        password="ValidPassword123!",
    )
    response = Response()
    register_user(payload=payload, response=response, db=db_session)

    # Second registration with same email should raise ConflictException
    with pytest.raises(ConflictException) as exc_info:
        register_user(payload=payload, response=response, db=db_session)

    assert "already exists" in str(exc_info.value.message)


def test_user_login_success(db_session):
    reg_payload = UserRegisterRequest(
        email="login_test@example.com",
        password="Password123!",
    )
    register_user(payload=reg_payload, response=Response(), db=db_session)

    login_payload = UserLoginRequest(
        email="login_test@example.com",
        password="Password123!",
    )
    response = Response()
    result = login_user(payload=login_payload, response=response, db=db_session)

    assert result.access_token is not None
    assert result.user.email == "login_test@example.com"


def test_user_login_invalid_credentials(db_session):
    # Non-existent email
    with pytest.raises(UnauthorizedException):
        login_user(
            payload=UserLoginRequest(email="nonexistent@example.com", password="pwd"),
            response=Response(),
            db=db_session,
        )

    # Wrong password
    reg_payload = UserRegisterRequest(
        email="wrong_pwd@example.com",
        password="CorrectPassword123!",
    )
    register_user(payload=reg_payload, response=Response(), db=db_session)

    with pytest.raises(UnauthorizedException):
        login_user(
            payload=UserLoginRequest(email="wrong_pwd@example.com", password="WrongPassword!"),
            response=Response(),
            db=db_session,
        )


def test_logout_response():
    response = Response()
    result = logout_user(response=response)
    assert result["message"] == "Logged out successfully."


def test_get_current_user_dependency(db_session):
    user = User(email="auth_dep@example.com", password_hash=get_password_hash("test"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(subject=user.id)

    # Mock request with no cookies
    scope = {"type": "http", "headers": []}
    req = Request(scope)

    # Valid token
    resolved_user = get_current_user(request=req, token=token, db=db_session)
    assert resolved_user.id == user.id

    # Missing token
    with pytest.raises(UnauthorizedException):
        get_current_user(request=req, token=None, db=db_session)

    # Invalid token
    with pytest.raises(UnauthorizedException):
        get_current_user(request=req, token="invalid.jwt.token", db=db_session)

