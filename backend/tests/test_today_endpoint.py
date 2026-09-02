import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import Base, SportEvent
from app.events.router import get_provider, get_session
from app.main import app
from app.sports.models import SportEvent as DomainEvent

from tests.conftest import make_test_engine


def make_domain_event(id, league, sport="futbol", home="A", away="B"):
    return DomainEvent(
        id=id,
        sport=sport,
        league=league,
        start_time_utc=dt.datetime.now(dt.UTC) + dt.timedelta(hours=3),
        status="programado",
        home_team=home,
        away_team=away,
    )


class FakeProvider:
    def __init__(self, events):
        self._events = events

    async def get_day_events(self, date, sport):
        return [e for e in self._events if e.sport == sport]

    async def get_event_result(self, event):
        raise NotImplementedError


async def _reset_schema():
    engine = make_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def _count_events() -> int:
    engine = make_test_engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            result = await session.execute(select(SportEvent))
            return len(result.scalars().all())
    finally:
        await engine.dispose()


@pytest.fixture
def client():
    asyncio.run(_reset_schema())

    async def override_session():
        engine = make_test_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    fake = FakeProvider(
        [
            make_domain_event("1", "Liga Profesional"),
            make_domain_event("2", "Premier League", home="C", away="D"),
            make_domain_event("3", "LaLiga", home="E", away="F"),
        ]
    )
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_provider] = lambda: fake
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_today_endpoint_persists_and_returns_curated(client):
    response = client.get("/events/today")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert body[0]["provider_event_id"] == "1"
    assert asyncio.run(_count_events()) == 3


def test_today_endpoint_is_idempotent(client):
    client.get("/events/today")
    client.get("/events/today")

    assert asyncio.run(_count_events()) == 3
