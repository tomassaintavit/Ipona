import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import Base, LLMCall, Prediction, SportEvent, User
from app.deps import get_session
from app.llm.player import ensure_llm_user
from app.llm.router import get_llm_client
from app.main import app


class FakeLLMClient:
    def __init__(self):
        self.calls = 0

    async def complete_json(self, system_prompt, user_prompt, session) -> dict:
        self.calls += 1
        session.add(
            LLMCall(
                provider="fake",
                model="fake-model",
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
            )
        )
        await session.commit()
        return {
            "predicciones": [
                {"event_id": 1, "home_score": 2, "away_score": 1},
                {"event_id": 2, "positions": ["P1", "P2", "P3"]},
                {"event_id": 999, "home_score": 0, "away_score": 0},
            ]
        }


async def _seed():
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            future = dt.datetime.now(dt.UTC) + dt.timedelta(hours=3)
            session.add_all(
                [
                    SportEvent(
                        provider="espn",
                        provider_event_id="fut1",
                        sport="futbol",
                        league="Liga",
                        start_time_utc=future,
                        status="programado",
                        home_team="Barracas",
                        away_team="Platense",
                    ),
                    SportEvent(
                        provider="espn",
                        provider_event_id="f1-1",
                        sport="formula_1",
                        league="F1",
                        start_time_utc=future,
                        status="programado",
                        participants=["P1", "P2", "P3"],
                    ),
                ]
            )
            await session.commit()
    finally:
        await engine.dispose()


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def client():
    asyncio.run(_seed())

    async def override_session():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    fake = FakeLLMClient()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_llm_client] = lambda: fake
    with TestClient(app) as c:
        c.fake = fake
        yield c
    app.dependency_overrides.clear()


def test_predict_genera_y_persiste_predicciones(client):
    response = client.post("/llm/predict")

    assert response.status_code == 200
    assert response.json()["predicciones_generadas"] == 2

    async def check():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                llm = (
                    await session.execute(select(User).where(User.username == "ipona-ia"))
                ).scalar_one()
                assert llm.is_llm is True
                preds = (
                    await session.execute(select(Prediction).where(Prediction.user_id == llm.id))
                ).scalars().all()
                assert len(preds) == 2
                calls = (await session.execute(select(LLMCall))).scalars().all()
                assert len(calls) == 1
                assert calls[0].total_tokens == 15
        finally:
            await engine.dispose()

    asyncio.run(check())


def test_predict_es_idempotente(client):
    first = client.post("/llm/predict")
    second = client.post("/llm/predict")

    assert first.json()["predicciones_generadas"] == 2
    assert second.json()["predicciones_generadas"] == 0
