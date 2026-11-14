from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.services.auth_service import decode_access_token
from src.services.builder_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_token_from_request(request: Request, bearer_token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """Extract token from Authorization header or cookie."""
    if bearer_token:
        return bearer_token
    # Check cookie fallback for browser UI
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token[7:]
        return cookie_token
    return None


def get_current_user(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT token and return authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Return user if authenticated, or None if anonymous."""
    if not token:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        user_id = int(user_id_str)
        return get_user_by_id(db, user_id=user_id)
    except Exception:
        return None


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure authenticated user is an administrator."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
