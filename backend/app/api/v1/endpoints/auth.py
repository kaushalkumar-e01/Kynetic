from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.errors import ConflictException, UnauthorizedException
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserProfile
from app.models.activity import UserActivity
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register_user(payload: UserRegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if existing_user:
        raise ConflictException(f"An account with email '{payload.email}' already exists.")

    hashed_password = get_password_hash(payload.password)
    user = User(
        email=payload.email.lower().strip(),
        password_hash=hashed_password,
        account_status="active",
    )
    db.add(user)
    db.flush()

    # Create associated profile
    profile = UserProfile(
        user_id=user.id,
        display_name=payload.display_name.strip() if payload.display_name else None,
    )
    db.add(profile)

    # Record registration activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="account_registered",
        details={"email": user.email},
    )
    db.add(activity)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)

    # Set HttpOnly cookie for web clients
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.APP_ENV != "development",
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain access token",
)
def login_user(payload: UserLoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password.")

    if user.account_status != "active":
        raise UnauthorizedException(f"Account is {user.account_status}. Please contact support.")

    # Record login activity
    activity = UserActivity(
        user_id=user.id,
        activity_type="user_logged_in",
    )
    db.add(activity)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id)

    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.APP_ENV != "development",
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    summary="Log out user and invalidate cookie",
)
def logout_user(response: Response):
    response.delete_cookie(key="access_token", samesite="lax")
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

