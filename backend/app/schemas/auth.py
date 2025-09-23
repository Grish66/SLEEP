from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from jwt import InvalidTokenError



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


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class AccessTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


