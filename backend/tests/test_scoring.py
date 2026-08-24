import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import Base, Prediction, SportEvent, User
from app.deps import get_provider, get_session
from app.main import app
from app.scoring.points import compute_points
from app.scoring.service import update_results


def make_event(**kwargs):
    defaults = dict(
        provider="espn",
        provider_event_id="e1",
        sport="futbol",
        league="Liga",
        start_time_utc=dt.datetime(2026, 8, 23, 20, 0, tzinfo=dt.UTC),
        status="finalizado",
        home_team="A",
        away_team="B",
        final_home_score=2,
        final_away_score=1,
    )
    defaults.update(kwargs)
    return SportEvent(**defaults)


def make_prediction(**kwargs):
    defaults = dict(home_score=2, away_score=1)
    defaults.update(kwargs)
    return Prediction(user_id=1, event_id=1, **defaults)


class TestComputePoints:
    def test_marcador_exacto_da_3(self):
        event = make_event()
        assert compute_points(event, make_prediction()) == 3.0

    def test_acierto_de_resultado_da_1(self):
        event = make_event()
        prediction = make_prediction(home_score=1, away_score=0)
        assert compute_points(event, prediction) == 1.0

    def test_falla_da_0(self):
        event = make_event()
        prediction = make_prediction(home_score=0, away_score=2)
        assert compute_points(event, prediction) == 0.0

    def test_empate_acertado_sin_marcador_exacto_da_1(self):
        event = make_event(final_home_score=1, final_away_score=1)
        prediction = make_prediction(home_score=2, away_score=2)
        assert compute_points(event, prediction) == 1.0

    def test_empate_acertado_exacto_da_3(self):
        event = make_event(final_home_score=1, final_away_score=1)
        prediction = make_prediction(home_score=1, away_score=1)
        assert compute_points(event, prediction) == 3.0

    def test_sin_resultado_devuelve_none(self):
        event = make_event(final_home_score=None, final_away_score=None)
        assert compute_points(event, make_prediction()) is None

    def test_f1_podio_exacto_da_3(self):
        event = make_event(
            sport="formula_1",
            final_positions=["Piastri", "Norris", "Verstappen"],
        )
        prediction = make_prediction(
            home_score=None,
            away_score=None,
            positions=["Piastri", "Norris", "Verstappen"],
        )
        assert compute_points(event, prediction) == 3.0

    def test_f1_parcial_da_por_posicion(self):
        event = make_event(
            sport="formula_1",
            final_positions=["Piastri", "Norris", "Verstappen"],
        )
        prediction = make_prediction(
            home_score=None,
            away_score=None,
            positions=["Norris", "Leclerc", "Verstappen"],
        )
        assert compute_points(event, prediction) == 1.0

    def test_f1_sin_resultado_devuelve_none(self):
        event = make_event(sport="formula_1", final_positions=None)
        prediction = make_prediction(
            home_score=None, away_score=None, positions=["A"]
        )
        assert compute_points(event, prediction) is None


class FakeResultProvider:
    async def get_day_events(self, date, sport):
        return []

    async def get_event_result(self, event):
        from app.sports.models import EventResult

        if event.id == "fut1":
            return EventResult(
                event_id=event.id, completed=True, home_score=2, away_score=1
            )
        raise LookupError("no encontrado")


async def _seed():
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            user = User(email="s@ipona.ar", username="scorer", password_hash="x")
            llm = User(
                email="llm@ipona.ar",
                username="Cris el pulpo Paul",
                password_hash="x",
                is_llm=True,
            )
            past = dt.datetime.now(dt.UTC) - dt.timedelta(hours=4)
            event = SportEvent(
                provider="espn",
                provider_event_id="fut1",
                sport="futbol",
                league="Liga",
                start_time_utc=past,
                status="finalizado",
                home_team="A",
                away_team="B",
            )
            unknown_event = SportEvent(
                provider="espn",
                provider_event_id="desconocido",
                sport="futbol",
                league="Liga",
                start_time_utc=past,
                status="finalizado",
                home_team="X",
                away_team="Y",
            )
            session.add_all([user, llm, event, unknown_event])
            await session.flush()
            session.add_all(
                [
                    Prediction(user_id=user.id, event_id=event.id, home_score=2, away_score=1),
                    Prediction(user_id=llm.id, event_id=event.id, home_score=1, away_score=0),
                    Prediction(user_id=user.id, event_id=unknown_event.id, home_score=0, away_score=0),
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

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_provider] = lambda: FakeResultProvider()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_update_results_calcula_puntos(client):
    response = client.post("/leaderboard/update")

    assert response.status_code == 200

    async def check():
        engine = create_async_engine(get_settings().database_url)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                result = await session.execute(select(Prediction).order_by(Prediction.id))
                preds = result.scalars().all()
                points = [p.points for p in preds[:2]]
                assert points == [3.0, 1.0]
                assert preds[2].points is None
        finally:
            await engine.dispose()

    asyncio.run(check())


def test_leaderboard_ordena_por_puntos(client):
    client.post("/leaderboard/update")

    board = client.get("/leaderboard").json()

    assert len(board) == 2
    assert board[0]["username"] == "scorer"
    assert board[0]["total_points"] == 3.0
    assert board[0]["position"] == 1
    assert board[1]["username"] == "Cris el pulpo Paul"
    assert board[1]["total_points"] == 1.0
