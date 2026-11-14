from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    deployment = relationship("Deployment", back_populates="verifications")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
