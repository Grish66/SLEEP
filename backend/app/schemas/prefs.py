from pydantic import BaseModel, Field

# Outgoing shape (what the API returns)
class PrefsOut(BaseModel):
    sleep_minutes: int

# Incoming update (what the client sends)
class PrefsUpdate(BaseModel):
    sleep_minutes: int = Field(..., ge=1, le=240)  # allow 1–240 minutes
