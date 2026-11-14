from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    client_or_company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=False, index=True)
    ai_tech_used = Column(String(300), nullable=False, index=True)
    deployment_stage = Column(String(50), default="Production", nullable=False)
    problem_statement = Column(Text, nullable=False)
    solution_description = Column(Text, nullable=False)
    measurable_results = Column(Text, nullable=False)
    live_demo_url = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    verification_status = Column(String(50), default="PENDING", nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="deployments")
    verifications = relationship("Verification", back_populates="deployment", cascade="all, delete-orphan")
