from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings

# Create a single async engine for the app
engine = create_async_engine(
    settings.db_dsn_async,
    pool_pre_ping=True,   # checks connections before using them
    echo=False,           # set True to see SQL in logs
)

# Factory that yields AsyncSession objects
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Dependency for FastAPI routes (we'll use this soon)
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
