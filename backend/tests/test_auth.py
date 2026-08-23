import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import Base
from app.deps import get_session
from app.main import app
from app.users.router import router as users_router


async def _reset_schema():
    engine = create_async_engine(get_settings().database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def client():
    asyncio.run(_reset_schema())

    async def override_session():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register(client, email="tomi@ipona.ar", username="tomi", password="secreto123"):
    return client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password},
    )


def login(client, username="tomi", password="secreto123"):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_register_creates_user(client):
    response = register(client)

    assert response.status_code == 201
    assert response.json()["username"] == "tomi"


def test_register_rejects_duplicate_email_or_username(client):
    register(client)

    dup_email = register(client, email="otro@ipona.ar")
    assert dup_email.status_code == 409

    dup_username = register(client, username="tomi2")
    assert dup_username.status_code == 409


def test_register_validates_input(client):
    short_password = register(client, password="corto")
    assert short_password.status_code == 422

    bad_username = register(client, username="x")
    assert bad_username.status_code == 422

    bad_email = register(client, email="no-es-un-email")
    assert bad_email.status_code == 422


def test_login_returns_valid_token(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    token = response.json()["access_token"]
    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "tomi"


def test_login_rejects_bad_credentials(client):
    register(client)

    wrong_password = login(client, password="incorrecta1")
    assert wrong_password.status_code == 401

    unknown_user = login(client, username="nadie")
    assert unknown_user.status_code == 401


def test_me_requires_token(client):
    no_token = client.get("/users/me")
    assert no_token.status_code == 401

    bad_token = client.get("/users/me", headers={"Authorization": "Bearer no-es-valido"})
    assert bad_token.status_code == 401


def test_login_rate_limited(client):
    for i in range(6):
        last = client.post(
            "/auth/login", json={"username": f"u{i}", "password": "loquesea123"}
        )
    assert last.status_code == 429
