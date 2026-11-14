from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MembershipBase(BaseModel):
    membership_number: int
    tier: str
    badge_label: str
    is_active: bool


class MembershipOut(MembershipBase):
    id: int
    user_id: int
    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MembershipStats(BaseModel):
    total_granted: int
    max_slots: int
    slots_remaining: int
