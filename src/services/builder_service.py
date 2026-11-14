from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from src.models.user import User
from src.schemas.user import UserRegister, UserUpdate
from src.services.auth_service import hash_password, verify_password
from src.services.membership_service import allocate_founding_membership


def register_builder(db: Session, data: UserRegister) -> User:
    """Register a new builder and allocate their Founding Builder slot."""
    hashed_pwd = hash_password(data.password)
    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email.lower().strip(),
        password_hash=hashed_pwd,
        title=data.title,
        company=data.company,
        location=data.location,
        linkedin_url=data.linkedin_url,
        github_url=data.github_url,
        website_url=data.website_url,
        bio=data.bio,
        is_verified=False,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Allocate founding membership
    allocate_founding_membership(db, user.id)
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify email & password credentials."""
    user = db.query(User).options(joinedload(User.membership)).filter(User.email == email.lower().strip()).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Find user by ID with eager loaded relationships."""
    return (
        db.query(User)
        .options(joinedload(User.membership), joinedload(User.deployments))
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Find user by email."""
    return db.query(User).filter(User.email == email.lower().strip()).first()


def update_builder_profile(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    """Update profile fields for a builder."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def list_builders(db: Session, skip: int = 0, limit: int = 50, verified_only: bool = False) -> List[User]:
    """List builders for the directory."""
    query = db.query(User).options(joinedload(User.membership), joinedload(User.deployments))
    if verified_only:
        query = query.filter(User.is_verified.is_(True))
    return query.order_by(User.id.asc()).offset(skip).limit(limit).all()
