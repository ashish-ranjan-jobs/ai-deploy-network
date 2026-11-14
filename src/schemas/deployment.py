from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.schemas.user import UserOut


class DeploymentBase(BaseModel):
    title: str
    client_or_company: Optional[str] = None
    industry: str
    ai_tech_used: str
    deployment_stage: str = "Production"
    hardware_target: Optional[str] = "Cloud (GPU/vLLM)"
    problem_statement: str
    solution_description: str
    measurable_results: str
    live_demo_url: Optional[str] = None
    repo_url: Optional[str] = None


class DeploymentCreate(DeploymentBase):
    pass


class DeploymentUpdate(BaseModel):
    title: Optional[str] = None
    client_or_company: Optional[str] = None
    industry: Optional[str] = None
    ai_tech_used: Optional[str] = None
    deployment_stage: Optional[str] = None
    hardware_target: Optional[str] = None
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    measurable_results: Optional[str] = None
    live_demo_url: Optional[str] = None
    repo_url: Optional[str] = None


class DeploymentOut(DeploymentBase):
    id: int
    user_id: int
    is_verified: bool
    verification_status: str
    verification_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)
