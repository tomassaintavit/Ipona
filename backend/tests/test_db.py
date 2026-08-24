import datetime as dt

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.models import Base, Prediction, SportEvent, User


@pytest.fixture
async def db_engine():
    engine = create_async_engine(get_settings().database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


async def test_insert_and_query_prediction(db_engine):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        user = User(
            email="test@ipona.ar", username="tomi", password_hash="hash", is_llm=False
        )
        llm = User(email="llm@ipona.ar", username="Cris el pulpo Paul", password_hash="x", is_llm=True)
        event = SportEvent(
            provider_event_id="123",
            sport="futbol",
            league="Liga Profesional",
            start_time_utc=dt.datetime(2026, 8, 23, 17, 45, tzinfo=dt.UTC),
            status="programado",
            home_team="Barracas Central",
            away_team="Platense",
        )
        session.add_all([user, llm, event])
        await session.flush()
        prediction = Prediction(
            user_id=user.id, event_id=event.id, home_score=2, away_score=1
        )
        session.add(prediction)
        await session.commit()

    async with session_factory() as session:
        result = await session.execute(
            select(Prediction).where(Prediction.home_score == 2)
        )
        found = result.scalar_one()
        assert found.user_id == user.id
        assert found.event_id == event.id

        llm_users = await session.execute(select(User).where(User.is_llm.is_(True)))
        assert llm_users.scalar_one().username == "Cris el pulpo Paul"
