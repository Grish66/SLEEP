from pydantic import BaseModel, Field
from typing import Optional


# Incoming payload to create a note
class NoteCreate(BaseModel):
    title: str = Field(..., max_length=200)
    body: str
    done: bool = False


# Incoming payload to update a note (all fields optional)
class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    body: Optional[str] = None
    done: Optional[bool] = None


# Outgoing shape returned by the API
class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    done: bool
