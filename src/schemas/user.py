from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.schemas.membership import MembershipOut


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    bio: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    bio: Optional[str] = None


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website_url: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    is_admin: bool
    created_at: datetime
    membership: Optional[MembershipOut] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
