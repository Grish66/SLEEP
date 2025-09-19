from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Incoming payload for signup
class SignupIn(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str


# Outgoing user info (safe to return)
class UserOut(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    verified: bool
    created_at: datetime
