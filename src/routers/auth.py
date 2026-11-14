from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.routers.deps import get_current_user
from src.schemas.user import Token, UserLogin, UserOut, UserRegister
from src.services.auth_service import create_access_token
from src.services.builder_service import authenticate_user, get_user_by_email, register_builder

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    """Register a new builder account and receive permanent Founding Builder status."""
    existing_user = get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A builder with this email is already registered",
        )

    user = register_builder(db, data)
    token = create_access_token(data={"sub": str(user.id)})

    # Also set secure cookie for browser web sessions
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        max_age=86400,
    )

    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticate builder credentials and return JWT token."""
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        max_age=86400,
    )

    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserOut.model_validate(current_user)


@router.post("/logout")
def logout(response: Response):
    """Log out user and clear session cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}
