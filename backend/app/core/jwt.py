from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jwt import InvalidTokenError
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


def decode_token(token: str, expected_type: str | None = None) -> dict:
    """
    Decode & verify a JWT. Optionally enforce token 'type' (e.g., 'access' or 'refresh').
    Raises jwt.InvalidTokenError if verification fails.
    """
    # Verify signature & standard claims (exp, iat, nbf)
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])

    # Optionally enforce expected type
    if expected_type is not None and payload.get("type") != expected_type:
        raise InvalidTokenError(f"Unexpected token type: {payload.get('type')!r}")

    return payload
