import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.models import Base, LLMCall, Prediction, SportEvent, User
from app.deps import get_session
from app.main import app


async def _seed():
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            user = User(
                email="s@ipona.ar", username="statsuser", password_hash="x"
            )
            llm = User(
                email="llm@ipona.ar",
                username="ipona-ia",
                password_hash="x",
                is_llm=True,
            )
            past = dt.datetime.now(dt.UTC) - dt.timedelta(days=2)

            def event(pid, sport, home="A", away="B"):
                return SportEvent(
                    provider="espn",
                    provider_event_id=pid,
                    sport=sport,
                    league="L",
                    start_time_utc=past,
                    status="finalizado",
                    home_team=home,
                    away_team=away,
                )

            futbol1 = event("f1", "futbol")
            futbol2 = event("f2", "futbol", "C", "D")
            f1race = event("r1", "formula_1")
            f1race.final_positions = ["P1", "P2", "P3"]
            session.add_all([user, llm, futbol1, futbol2, f1race])
            await session.flush()

            def pred(uid, eid, **kw):
                return Prediction(user_id=uid, event_id=eid, **kw)

            session.add_all(
                [
                    pred(user.id, futbol1.id, home_score=1, away_score=0, points=3.0),
                    pred(user.id, futbol2.id, home_score=0, away_score=2, points=1.0),
                    pred(
                        user.id,
                        f1race.id,
                        positions=["P1", "X", "X"],
                        points=1.0,
                    ),
                    pred(llm.id, futbol1.id, home_score=9, away_score=9, points=1.0),
                    LLMCall(provider="groq", model="m", prompt_tokens=100, completion_tokens=50, total_tokens=150),
                    LLMCall(provider="cerebras", model="m", prompt_tokens=30, completion_tokens=20, total_tokens=50),
                ]
            )
            await session.commit()
            return user.id
    finally:
        await engine.dispose()


@pytest.fixture
def client():
    user_id = asyncio.run(_seed())

    async def override_session():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    headers = {"Authorization": f"Bearer {create_access_token(user_id)}"}
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        c.headers.update(headers)
        yield c
    app.dependency_overrides.clear()


def test_my_stats_agrupa_por_deporte(client):
    response = client.get("/stats/me")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "statsuser"
    assert body["predicciones"] == 3
    assert body["aciertos"] == 3
    assert abs(body["precision"] - 1.0) < 0.001

    deportes = {s["sport"]: s for s in body["por_deporte"]}
    assert deportes["futbol"]["predicciones"] == 2
    assert deportes["futbol"]["marcadores_exactos"] == 1
    assert deportes["futbol"]["puntos"] == 4.0
    assert deportes["formula_1"]["aciertos"] == 1
    assert deportes["formula_1"]["marcadores_exactos"] == 0


def test_llm_stats_incluye_tokens(client):
    response = client.get("/stats/llm")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "ipona-ia"
    assert body["predicciones"] == 1
    assert body["tokens"]["llamadas"] == 2
    assert body["tokens"]["total"] == 200


def test_stats_requieren_token():
    async def override_session():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as anonymous:
            no_token = anonymous.get("/stats/me")
    finally:
        app.dependency_overrides.clear()
    assert no_token.status_code == 401
