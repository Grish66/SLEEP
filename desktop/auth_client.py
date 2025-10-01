import httpx
import keyring
from typing import Any, Dict, Optional

API_BASE = "http://127.0.0.1:8000"
KEYRING_SERVICE = "SLEEP"


async def _refresh_access_token(email: str) -> Optional[str]:
    """
    Use the stored refresh token to get a new access token.
    Returns the new access token (also saves it) or None on failure.
    """
    refresh = keyring.get_password(KEYRING_SERVICE, f"{email}:refresh")
    if not refresh:
        return None

    async with httpx.AsyncClient(base_url=API_BASE, timeout=15) as client:
        resp = await client.post("/auth/refresh", json={"refresh_token": refresh})
    if resp.status_code != 200:
        return None

    new_access = resp.json().get("access_token")
    if not new_access:
        return None

    keyring.set_password(KEYRING_SERVICE, f"{email}:access", new_access)
    return new_access


async def get_me(email: str) -> Dict[str, Any]:
    """
    Call GET /me using the stored access token.
    If unauthorized, try refreshing the access token once and retry.
    Raises httpx.HTTPStatusError on failure.
    """
    access = keyring.get_password(KEYRING_SERVICE, f"{email}:access")
    if not access:
        raise RuntimeError("No access token found. Please login first.")

    async with httpx.AsyncClient(base_url=API_BASE, timeout=15) as client:
        # First try with current access token
        resp = await client.get("/me", headers={"Authorization": f"Bearer {access}"})
        if resp.status_code == 200:
            return resp.json()

        # If token is invalid/expired, try to refresh once
        if resp.status_code == 401:
            new_access = await _refresh_access_token(email)
            if not new_access:
                # Still unauthorized; bubble up
                resp.raise_for_status()
            # Retry with refreshed access token
            resp2 = await client.get("/me", headers={"Authorization": f"Bearer {new_access}"})
            if resp2.status_code == 200:
                return resp2.json()
            resp2.raise_for_status()

        # Any other error -> raise
        resp.raise_for_status()
