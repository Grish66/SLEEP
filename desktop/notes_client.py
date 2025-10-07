import httpx
import keyring
from typing import Any, List, Optional

from auth_client import _refresh_access_token  # reuse our refresh helper

API_BASE = "http://127.0.0.1:8000"
KEYRING_SERVICE = "SLEEP"


async def list_notes(email: str) -> List[dict]:
    access = keyring.get_password(KEYRING_SERVICE, f"{email}:access")
    if not access:
        raise RuntimeError("No access token found. Please login first.")

    async with httpx.AsyncClient(base_url=API_BASE, timeout=20) as client:
        resp = await client.get("/notes", headers={"Authorization": f"Bearer {access}"})
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 401:
            new_access: Optional[str] = await _refresh_access_token(email)
            if not new_access:
                resp.raise_for_status()
            resp2 = await client.get("/notes", headers={"Authorization": f"Bearer {new_access}"})
            if resp2.status_code == 200:
                return resp2.json()
            resp2.raise_for_status()
        resp.raise_for_status()


async def create_note(email: str, title: str, body: str, done: bool = False) -> dict:
    """
    Create a note via POST /notes, using stored access token; refresh once on 401.
    Returns the created note dict.
    """
    access = keyring.get_password(KEYRING_SERVICE, f"{email}:access")
    if not access:
        raise RuntimeError("No access token found. Please login first.")

    payload = {"title": title, "body": body, "done": done}

    async with httpx.AsyncClient(base_url=API_BASE, timeout=20) as client:
        resp = await client.post("/notes", json=payload, headers={"Authorization": f"Bearer {access}"})
        if resp.status_code in (200, 201):
            return resp.json()

        if resp.status_code == 401:
            new_access: Optional[str] = await _refresh_access_token(email)
            if not new_access:
                resp.raise_for_status()
            resp2 = await client.post("/notes", json=payload, headers={"Authorization": f"Bearer {new_access}"})
            if resp2.status_code in (200, 201):
                return resp2.json()
            resp2.raise_for_status()

        resp.raise_for_status()
