from typing import Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # First priority: Authorization header (via oauth2_scheme)
    # Second priority: HttpOnly cookie 'access_token'
    auth_token = token
    if not auth_token:
        auth_token = request.cookies.get("access_token")

    if not auth_token:
        raise UnauthorizedException("Authentication token is missing. Please log in.")

    payload = decode_access_token(auth_token)
    if not payload:
        raise UnauthorizedException("Invalid or expired authentication token.")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token payload missing subject.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User associated with this token does not exist.")

    if user.account_status != "active":
        raise UnauthorizedException(f"Account is currently {user.account_status}.")

    return user
