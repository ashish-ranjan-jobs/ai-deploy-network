from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class VerificationReview(BaseModel):
    status: Literal["APPROVED", "REJECTED"]
    feedback_notes: Optional[str] = None


class VerificationOut(BaseModel):
    id: int
    deployment_id: int
    reviewer_id: Optional[int] = None
    status: str
    feedback_notes: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
