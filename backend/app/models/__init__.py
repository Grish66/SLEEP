from sqlalchemy.orm import DeclarativeBase

# Define Base FIRST so submodules can import it
class Base(DeclarativeBase):
    pass

# Import models AFTER Base is defined, so Alembic can discover them
from .user import User  # noqa: F401
from .note import Note  # noqa: F401
