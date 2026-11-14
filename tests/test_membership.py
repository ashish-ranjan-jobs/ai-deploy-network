from sqlalchemy.orm import Session

from src.models.user import User
from src.services.auth_service import hash_password
from src.services.membership_service import allocate_founding_membership, get_membership_stats


def test_membership_slot_allocation(db_session: Session):
    # Create multiple users and verify sequential membership numbers
    user1 = User(first_name="User1", last_name="Test", email="u1@test.com", password_hash=hash_password("pw"))
    user2 = User(first_name="User2", last_name="Test", email="u2@test.com", password_hash=hash_password("pw"))
    db_session.add_all([user1, user2])
    db_session.commit()

    m1 = allocate_founding_membership(db_session, user1.id)
    m2 = allocate_founding_membership(db_session, user2.id)

    assert m1.membership_number == 1
    assert m1.tier == "Founding Builder"
    assert m1.badge_label == "Founding Builder #001"

    assert m2.membership_number == 2
    assert m2.tier == "Founding Builder"
    assert m2.badge_label == "Founding Builder #002"

    stats = get_membership_stats(db_session)
    assert stats.total_granted == 2
    assert stats.slots_remaining == 498
