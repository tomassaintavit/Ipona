import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.battles.service import (
    create_daily_battles,
    get_week_battles,
    resolve_battles,
    set_battle_message,
)
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.db.models import Base, Battle, Prediction, SportEvent, User
from app.deps import get_provider, get_session
from app.main import app


async def _seed():
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            users = [
                User(email="a@ipona.ar", username="alberto", password_hash="x"),
                User(email="b@ipona.ar", username="belen", password_hash="x"),
                User(email="c@ipona.ar", username="carlos", password_hash="x"),
                User(
                    email="llm@ipona.ar",
                    username="Cris el pulpo Paul",
                    password_hash="x",
                    is_llm=True,
                ),
            ]
            session.add_all(users)
            await session.commit()
            return [u.id for u in users]
    finally:
        await engine.dispose()


def _make_factory():
    engine = create_async_engine(get_settings().database_url)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def test_empareja_usuario_y_ia_juntos():
    ids = await _seed()
    engine, factory = _make_factory()
    try:
        async with factory() as session:
            battles = await create_daily_battles(session, dt.date(2026, 9, 3))
            assert len(battles) == 2
            participantes = set()
            for b in battles:
                participantes.add(b.user_a_id)
                if b.user_b_id:
                    participantes.add(b.user_b_id)
                if b.extra_user_id:
                    participantes.add(b.extra_user_id)
            assert participantes == set(ids)
            # 4 jugadores -> 2 battles de a 2, ninguna trío
            assert all(b.extra_user_id is None for b in battles)
    finally:
        await engine.dispose()


async def test_impares_forma_un_trio_en_la_ultima():
    engine, factory = _make_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            ids = []
            for i in range(5):
                u = User(
                    email=f"u{i}@ipona.ar",
                    username=f"usuario{i}",
                    password_hash="x",
                )
                session.add(u)
                await session.flush()
                ids.append(u.id)
            await session.commit()
            battles = await create_daily_battles(session, dt.date(2026, 9, 3))
            assert len(battles) == 2
            trios = [b for b in battles if b.extra_user_id is not None]
            pares = [b for b in battles if b.extra_user_id is None]
            assert len(trios) == 1 and len(pares) == 1
            cubre = set()
            for b in battles:
                cubre.add(b.user_a_id)
                cubre.add(b.user_b_id)
                if b.extra_user_id:
                    cubre.add(b.extra_user_id)
            assert cubre == set(ids)
    finally:
        await engine.dispose()


async def test_no_duplica_battles_para_la_misma_fecha():
    ids = await _seed()
    engine, factory = _make_factory()
    try:
        async with factory() as session:
            await create_daily_battles(session, dt.date(2026, 9, 3))
            otra_vez = await create_daily_battles(session, dt.date(2026, 9, 3))
            assert otra_vez == []
    finally:
        await engine.dispose()


async def test_resuelve_battle_con_ganador_y_permite_mensaje():
    ids = await _seed()
    engine, factory = _make_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            users = [
                User(email="a@ipona.ar", username="alberto", password_hash="x"),
                User(email="b@ipona.ar", username="belen", password_hash="x"),
            ]
            session.add_all(users)
            await session.flush()
            uid_a, uid_b = users[0].id, users[1].id
            battle = Battle(
                battle_date=dt.date(2026, 9, 3),
                user_a_id=uid_a,
                user_b_id=uid_b,
            )
            session.add(battle)
            hoy = dt.datetime(2026, 9, 3, 20, 0, tzinfo=dt.UTC)
            event = SportEvent(
                provider="espn",
                provider_event_id="fut1",
                sport="futbol",
                league="Liga",
                start_time_utc=hoy,
                status="finalizado",
                home_team="X",
                away_team="Y",
            )
            session.add(event)
            await session.flush()
            session.add_all(
                [
                    Prediction(user_id=uid_a, event_id=event.id, home_score=2, away_score=1, points=3.0),
                    Prediction(user_id=uid_b, event_id=event.id, home_score=0, away_score=0, points=0.0),
                ]
            )
            await session.commit()

            resolved = await resolve_battles(session, dt.date(2026, 9, 3))
            assert resolved == 1
            await session.refresh(battle)
            assert battle.status == "resuelta"
            assert battle.winner_id == uid_a

            b = await set_battle_message(session, battle.id, uid_a, "gané!")
            assert b.message == "gané!"

            # el perdedor no puede escribir
            with pytest.raises(Exception):
                await set_battle_message(session, battle.id, uid_b, "no")
    finally:
        await engine.dispose()


async def test_ia_no_escribe_mensajes():
    ids = await _seed()
    engine, factory = _make_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            llm = User(
                email="llm@ipona.ar",
                username="Cris el pulpo Paul",
                password_hash="x",
                is_llm=True,
            )
            human = User(email="h@ipona.ar", username="humano", password_hash="x")
            session.add_all([llm, human])
            await session.flush()
            battle = Battle(
                battle_date=dt.date(2026, 9, 3),
                user_a_id=human.id,
                user_b_id=llm.id,
            )
            session.add(battle)
            await session.commit()

            # si la IA gana la battle, queda sin message
            async def _win():
                async with engine.begin() as conn:
                    pass
            battle.winner_id = llm.id
            battle.status = "resuelta"
            await session.commit()

            with pytest.raises(Exception):
                await set_battle_message(session, battle.id, llm.id, "hola")
    finally:
        await engine.dispose()


async def test_empate_no_declara_ganador():
    ids = await _seed()
    engine, factory = _make_factory()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            u1 = User(email="u1@ipona.ar", username="uno", password_hash="x")
            u2 = User(email="u2@ipona.ar", username="dos", password_hash="x")
            session.add_all([u1, u2])
            await session.flush()
            battle = Battle(
                battle_date=dt.date(2026, 9, 3),
                user_a_id=u1.id,
                user_b_id=u2.id,
            )
            session.add(battle)
            hoy = dt.datetime(2026, 9, 3, 20, 0, tzinfo=dt.UTC)
            event = SportEvent(
                provider="espn",
                provider_event_id="fut1",
                sport="futbol",
                league="Liga",
                start_time_utc=hoy,
                status="finalizado",
                home_team="X",
                away_team="Y",
            )
            session.add(event)
            await session.flush()
            session.add_all(
                [
                    Prediction(user_id=u1.id, event_id=event.id, home_score=1, away_score=0, points=3.0),
                    Prediction(user_id=u2.id, event_id=event.id, home_score=2, away_score=1, points=3.0),
                ]
            )
            await session.commit()

            resolved = await resolve_battles(session, dt.date(2026, 9, 3))
            assert resolved == 1
            await session.refresh(battle)
            assert battle.status == "resuelta"
            assert battle.winner_id is None
    finally:
        await engine.dispose()


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


def test_endpoints_battles_requieren_auth():
    with TestClient(app) as c:
        assert c.get("/battles/today").status_code == 401
        assert c.get("/battles/week").status_code == 401
        assert c.post("/battles/message", json={"battle_id": 1, "message": "x"}).status_code == 401


def test_leaderboard_periodo_invalido():
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_session():
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_provider] = lambda: None
    try:
        async def seed():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            async with factory() as session:
                user = User(email="lb@ipona.ar", username="lider", password_hash="x")
                session.add(user)
                await session.commit()
                return user.id

        user_id = asyncio.run(seed())
        headers = {"Authorization": f"Bearer {create_access_token(user_id)}"}
        with TestClient(app) as c:
            c.headers.update(headers)
            assert c.get("/leaderboard?period=anual").status_code == 400
            assert c.get("/leaderboard?period=weekly").status_code == 200
            assert c.get("/leaderboard?period=monthly").status_code == 200
            assert c.get("/leaderboard?period=global").status_code == 200
    finally:
        app.dependency_overrides.clear()
        asyncio.run(engine.dispose())


def test_flujo_endpoint_battles_today_mensaje():
    def _factory():
        e = create_async_engine(get_settings().database_url)
        return e, async_sessionmaker(e, expire_on_commit=False)

    async def seed():
        engine, factory = _factory()
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            async with factory() as session:
                a = User(email="a@ipona.ar", username="alberto", password_hash="x")
                b = User(email="b@ipona.ar", username="belen", password_hash="x")
                session.add_all([a, b])
                await session.flush()
                battle = Battle(
                    battle_date=dt.date.today(),
                    user_a_id=a.id,
                    user_b_id=b.id,
                    status="resuelta",
                    winner_id=a.id,
                )
                session.add(battle)
                hoy = dt.datetime.combine(dt.date.today(), dt.time(20, 0), tzinfo=dt.UTC)
                event = SportEvent(
                    provider="espn",
                    provider_event_id="fut1",
                    sport="futbol",
                    league="Liga",
                    start_time_utc=hoy,
                    status="finalizado",
                    home_team="X",
                    away_team="Y",
                )
                session.add(event)
                await session.flush()
                session.add_all(
                    [
                        Prediction(user_id=a.id, event_id=event.id, home_score=2, away_score=1, points=3.0),
                        Prediction(user_id=b.id, event_id=event.id, home_score=0, away_score=0, points=0.0),
                    ]
                )
                await session.commit()
                return a.id
        finally:
            await engine.dispose()

    async def override_session():
        engine, factory = _factory()
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_provider] = lambda: None
    try:
        aid = asyncio.run(seed())
        headers = {"Authorization": f"Bearer {create_access_token(aid)}"}
        with TestClient(app) as c:
            c.headers.update(headers)
            hoy = c.get("/battles/today").json()
            assert hoy["status"] == "resuelta"
            assert hoy["winner"] == "me"
            assert hoy["winner_message"] is None
            assert hoy["my_points"] == 3.0
            assert hoy["opponent_points"] == 0.0

            r = c.post(
                "/battles/message",
                json={"battle_id": hoy["battle_id"], "message": "buena partida!"},
            )
            assert r.status_code == 200
            assert r.json()["winner_message"] == "buena partida!"

            semana = c.get("/battles/week").json()
            assert len(semana) == 1
            assert semana[0]["result"] == "gane"

            r2 = c.post(
                "/battles/message",
                json={"battle_id": hoy["battle_id"], "message": "otra vez"},
            )
            assert r2.status_code == 400
    finally:
        app.dependency_overrides.clear()
