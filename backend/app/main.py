from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.session import get_session
from app.core.security import hash_password, verify_password 
from app.core.jwt import create_access_token, create_refresh_token     # <-- add
from app.schemas.auth import SignupIn, UserOut, LoginIn, TokenPair
from app.schemas.auth import SignupIn, UserOut
from app.models import User

app = FastAPI(title=settings.app_name)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "env": settings.app_env}

@app.get("/db/ping")
async def db_ping(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    return {"db": "ok" if value == 1 else "fail"}

@app.post("/auth/signup", response_model=UserOut, status_code=201)
async def auth_signup(payload: SignupIn, session: AsyncSession = Depends(get_session)):
    # 1) Email already taken?
    exists = await session.execute(select(User).where(User.email == payload.email))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # 2) Create user with hashed password
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    await session.flush()     # get DB-generated values (id, created_at server_default)
    await session.commit()
    await session.refresh(user)

    # 3) Return safe shape
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        verified=user.verified,
        created_at=user.created_at,
    )


@app.post("/auth/login", response_model=TokenPair)
async def auth_login(payload: LoginIn, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        # same message for both cases to avoid leaking which part failed
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user_id=user.id, email=user.email)
    refresh = create_refresh_token(user_id=user.id)
    return TokenPair(access_token=access, refresh_token=refresh)