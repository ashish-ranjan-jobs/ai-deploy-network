from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    membership_number = Column(Integer, unique=True, index=True, nullable=False)
    tier = Column(String(50), default="Founding Builder", nullable=False)
    badge_label = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="membership")

    @property
    def formatted_number(self) -> str:
        return f"#{self.membership_number:03d}"
