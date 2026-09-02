import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.rate_limit import limiter
from app.db.models import Base, SportEvent, User
from app.deps import get_session
from app.main import app

from tests.conftest import make_test_engine


async def _seed():
    engine = make_test_engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            user = User(
                email="p@ipona.ar", username="predador", password_hash="x"
            )
            future = dt.datetime.now(dt.UTC) + dt.timedelta(hours=3)
            past = dt.datetime.now(dt.UTC) - dt.timedelta(hours=2)
            events = [
                SportEvent(
                    provider="espn",
                    provider_event_id="fut1",
                    sport="futbol",
                    league="Liga",
                    start_time_utc=future,
                    status="programado",
                    home_team="A",
                    away_team="B",
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
                SportEvent(
                    provider="espn",
                    provider_event_id="fut2",
                    sport="futbol",
                    league="Liga",
                    start_time_utc=past,
                    status="en_curso",
                    home_team="C",
                    away_team="D",
                ),
                SportEvent(
                    provider="espn",
                    provider_event_id="fut3",
                    sport="futbol",
                    league="Liga",
                    start_time_utc=dt.datetime.now(dt.UTC) - dt.timedelta(days=2),
                    status="finalizado",
                    home_team="E",
                    away_team="F",
                    final_home_score=3,
                    final_away_score=1,
                ),
            ]
            session.add_all([user, *events])
            await session.commit()
            return user.id
    finally:
        await engine.dispose()


def seed():
    return asyncio.run(_seed())


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def client():
    user_id = seed()

    async def override_session():
        engine = make_test_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    from app.core.security import create_access_token

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        c.headers.update(headers)
        yield c
    app.dependency_overrides.clear()


def event_id_by_provider(client, provider_event_id):
    # los ids se asignan secuencialmente: fut1=1, f1-1=2, fut2=3, fut3=4
    return {"fut1": 1, "f1-1": 2, "fut2": 3, "fut3": 4}[provider_event_id]


def test_guarda_prediccion_de_futbol(client):
    response = client.post(
        "/predictions",
        json={"event_id": 1, "home_score": 2, "away_score": 1},
    )
    assert response.status_code == 201
    assert response.json()["home_score"] == 2


def test_rechaza_marcador_para_f1_y_posiciones_para_futbol(client):
    scores_on_f1 = client.post(
        "/predictions", json={"event_id": 2, "home_score": 1, "away_score": 0}
    )
    assert scores_on_f1.status_code == 422

    positions_on_football = client.post(
        "/predictions", json={"event_id": 1, "positions": ["P1", "P2"]}
    )
    assert positions_on_football.status_code == 422


def test_rechaza_payload_vacio_o_mixto(client):
    vacio = client.post("/predictions", json={"event_id": 1})
    assert vacio.status_code == 422

    mixto = client.post(
        "/predictions",
        json={"event_id": 1, "home_score": 1, "away_score": 0, "positions": ["P1"]},
    )
    assert mixto.status_code == 422


def test_actualiza_prediccion_existente(client):
    first = client.post(
        "/predictions", json={"event_id": 1, "home_score": 1, "away_score": 1}
    )
    second = client.post(
        "/predictions", json={"event_id": 1, "home_score": 3, "away_score": 0}
    )

    assert first.status_code == 201
    assert second.status_code == 201

    mine = client.get("/predictions/my").json()
    assert len(mine) == 1
    assert mine[0]["home_score"] == 3


def test_bloquea_prediccion_despues_del_inicio(client):
    response = client.post(
        "/predictions", json={"event_id": 3, "home_score": 0, "away_score": 0}
    )
    assert response.status_code == 403


def test_evento_inexistente_da_404(client):
    response = client.post(
        "/predictions", json={"event_id": 999, "home_score": 0, "away_score": 0}
    )
    assert response.status_code == 404


def test_my_predictions_sin_token_da_401():
    async def override_session():
        engine = make_test_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as anonymous:
            response = anonymous.get("/predictions/my")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 401


def _seed_finalizada_prediction():
    from app.db.models import Prediction

    async def add():
        engine = make_test_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                user = (await session.execute(select(User).where(User.username == "predador"))).scalar_one()
                session.add(
                    Prediction(
                        user_id=user.id,
                        event_id=4,
                        home_score=2,
                        away_score=0,
                        points=3.0,
                    )
                )
                await session.commit()
        finally:
            await engine.dispose()

    asyncio.run(add())


def test_history_solo_lista_predicciones_finalizadas(client):
    _seed_finalizada_prediction()
    response = client.get("/predictions/history")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 1
    item = items[0]
    assert item["teams"] == ["E", "F"]
    assert item["predicted_home"] == 2
    assert item["predicted_away"] == 0
    assert item["final_home"] == 3
    assert item["final_away"] == 1
    assert item["points"] == 3.0
    assert item["sport"] == "futbol"
