from typing import AsyncIterator

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.deps import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
@limiter.limit(get_settings().auth_rate_limit)
async def register(
    request: Request,
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    if not get_settings().invite_code:
        raise HTTPException(status_code=503, detail="registro deshabilitado")
    if payload.codigo_invitacion != get_settings().invite_code:
        raise HTTPException(status_code=403, detail="codigo de invitacion invalido")
    existing = await session.execute(
        select(User).where(
            (User.email == payload.email) | (User.username == payload.username)
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="email o username ya registrado")
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserOut(id=user.id, email=user.email, username=user.username)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(get_settings().auth_rate_limit)
async def login(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    result = await session.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="credenciales invalidas")
    return TokenResponse(access_token=create_access_token(user.id))


async def get_current_user(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="token faltante")
    token = authorization.removeprefix("Bearer ")
    try:
        user_id = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])["sub"]
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="token invalido")
    result = await session.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="usuario inexistente")
    return user
