from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from app.core.settings import settings


def _base_payload(user_id: int, email: str | None = None) -> Dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(user_id),         # subject = user id
        "iat": int(now.timestamp()), # issued at
        "nbf": int(now.timestamp()), # not before
    }
    if email:
        payload["email"] = email
    return payload


def create_access_token(user_id: int, email: str | None = None) -> str:
    """Short-lived token for API calls."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = _base_payload(user_id, email)
    payload.update({"type": "access", "exp": exp})
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def create_refresh_token(user_id: int) -> str:
    """Longer-lived token to mint new access tokens."""
    exp = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)
    payload = _base_payload(user_id)
    payload.update({"type": "refresh", "exp": exp})
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)
