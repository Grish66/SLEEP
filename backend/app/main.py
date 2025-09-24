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

from app.deps.auth import get_current_user_claims 

from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import SignupIn, UserOut, LoginIn, TokenPair, RefreshIn, AccessTokenOut

from app.schemas.note import NoteCreate, NoteOut
from app.models import Note



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


@app.get("/me")
async def read_me(claims: dict = Depends(get_current_user_claims)):
    """
    Example protected route. Requires Authorization: Bearer <access_token>
    """
    return {"user_id": claims["user_id"], "email": claims["email"]}



@app.post("/auth/refresh", response_model=AccessTokenOut)
async def auth_refresh(payload: RefreshIn, session: AsyncSession = Depends(get_session)):
    # 1) Verify the refresh token and read its subject (user id)
    try:
        data = decode_token(payload.refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = int(data["sub"])

    # 2) (Optional) fetch email so new access token includes it
    result = await session.execute(select(User.email).where(User.id == user_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    # 3) Issue a fresh access token
    new_access = create_access_token(user_id=user_id, email=email)
    return AccessTokenOut(access_token=new_access)


@app.post("/notes", response_model=NoteOut, status_code=201)
async def create_note(
    payload: NoteCreate,
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
):
    note = Note(
        user_id=claims["user_id"],
        title=payload.title,
        body=payload.body,
        done=payload.done,
    )
    session.add(note)
    await session.flush()
    await session.commit()
    await session.refresh(note)
    return NoteOut(id=note.id, title=note.title, body=note.body, done=note.done)


@app.get("/notes", response_model=list[NoteOut])
async def list_notes(
    claims: dict = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(Note).where(Note.user_id == claims["user_id"]).order_by(Note.id.desc())
    )
    notes = result.scalars().all()
    return [NoteOut(id=n.id, title=n.title, body=n.body, done=n.done) for n in notes]
