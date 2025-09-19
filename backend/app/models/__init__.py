from sqlalchemy.orm import DeclarativeBase

# Base for all ORM models
class Base(DeclarativeBase):
    pass

# Import models so Alembic can see them
from .user import User  # noqa: F401
