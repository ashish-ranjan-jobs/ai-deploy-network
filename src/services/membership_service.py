from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.config import get_settings
from src.models.membership import Membership
from src.schemas.membership import MembershipStats

settings = get_settings()


def allocate_founding_membership(db: Session, user_id: int) -> Optional[Membership]:
    """
    Allocate a permanent Founding Builder membership slot (1-500) if available.
    """
    # Check if user already has membership
    existing = db.query(Membership).filter(Membership.user_id == user_id).first()
    if existing:
        return existing

    # Count how many Founding Builders exist
    current_count = db.query(func.count(Membership.id)).scalar() or 0

    if current_count >= settings.MAX_FOUNDING_BUILDERS:
        # Slots full, create standard builder membership
        next_num = current_count + 1
        membership = Membership(
            user_id=user_id,
            membership_number=next_num,
            tier="Standard Builder",
            badge_label=f"Builder #{next_num:03d}",
            is_active=True,
        )
    else:
        # Founding Builder slot available
        next_num = current_count + 1
        membership = Membership(
            user_id=user_id,
            membership_number=next_num,
            tier="Founding Builder",
            badge_label=f"Founding Builder #{next_num:03d}",
            is_active=True,
        )

    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_membership_stats(db: Session) -> MembershipStats:
    """Return count of granted memberships and remaining Founding Builder slots."""
    total_granted = db.query(func.count(Membership.id)).scalar() or 0
    max_slots = settings.MAX_FOUNDING_BUILDERS
    remaining = max(0, max_slots - total_granted)
    return MembershipStats(
        total_granted=total_granted,
        max_slots=max_slots,
        slots_remaining=remaining,
    )


def get_user_membership(db: Session, user_id: int) -> Optional[Membership]:
    """Retrieve membership record for given user ID."""
    return db.query(Membership).filter(Membership.user_id == user_id).first()
