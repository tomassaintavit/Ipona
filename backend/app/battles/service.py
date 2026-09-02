import datetime as dt
import random

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Battle, Prediction, SportEvent, User

MAX_MESSAGE_LENGTH = 100


async def create_daily_battles(session: AsyncSession, date: dt.date) -> list[Battle]:
    """Genera emparejamientos aleatorios para una fecha (todas las battles nuevas)."""
    existing = await session.execute(
        select(Battle).where(Battle.battle_date == date)
    )
    if existing.scalars().first() is not None:
        return []

    result = await session.execute(
        select(User).where(User.created_at <= dt.datetime.combine(date, dt.time.max))
    )
    players = list(result.scalars())
    random.shuffle(players)

    battles: list[Battle] = []
    i = 0
    while i < len(players):
        remaining = len(players) - i
        if remaining == 3:
            battle = Battle(
                battle_date=date,
                user_a_id=players[i].id,
                user_b_id=players[i + 1].id,
                extra_user_id=players[i + 2].id,
            )
            i += 3
        elif remaining >= 2:
            battle = Battle(
                battle_date=date,
                user_a_id=players[i].id,
                user_b_id=players[i + 1].id,
            )
            i += 2
        else:
            break
        session.add(battle)
        battles.append(battle)

    await session.commit()
    return battles


async def _day_points(session: AsyncSession, user_id: int, date: dt.date) -> float:
    start = dt.datetime.combine(date, dt.time.min, tzinfo=dt.UTC)
    end = start + dt.timedelta(days=1)
    result = await session.execute(
        select(func.coalesce(func.sum(Prediction.points), 0.0))
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(
            Prediction.user_id == user_id,
            SportEvent.start_time_utc >= start,
            SportEvent.start_time_utc < end,
            Prediction.points.is_not(None),
        )
    )
    return float(result.scalar() or 0.0)


async def _all_scored(session: AsyncSession, user_ids: list[int], date: dt.date) -> bool:
    """True si todos los eventos del día del usuario están puntuados."""
    start = dt.datetime.combine(date, dt.time.min, tzinfo=dt.UTC)
    end = start + dt.timedelta(days=1)
    result = await session.execute(
        select(Prediction.id)
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(
            Prediction.user_id.in_(user_ids),
            SportEvent.start_time_utc >= start,
            SportEvent.start_time_utc < end,
            Prediction.points.is_(None),
        )
    )
    return result.first() is None


async def resolve_battles(session: AsyncSession, date: dt.date) -> int:
    """Resuelve las battles del día si todos los eventos estan puntuados."""
    result = await session.execute(
        select(Battle).where(Battle.battle_date == date, Battle.status == "pendiente")
    )
    battles = list(result.scalars())
    resolved = 0
    for battle in battles:
        user_ids = [battle.user_a_id]
        if battle.user_b_id:
            user_ids.append(battle.user_b_id)
        if battle.extra_user_id:
            user_ids.append(battle.extra_user_id)

        if not await _all_scored(session, user_ids, date):
            continue

        puntos = {uid: await _day_points(session, uid, date) for uid in user_ids}
        max_puntos = max(puntos.values())
        ganadores = [uid for uid, pts in puntos.items() if pts == max_puntos]

        if len(ganadores) == 1 and len(user_ids) > 1:
            battle.winner_id = ganadores[0]
        else:
            battle.winner_id = None
        battle.status = "resuelta"
        resolved += 1
    await session.commit()
    return resolved


async def set_battle_message(
    session: AsyncSession, battle_id: int, user_id: int, message: str
) -> Battle:
    if len(message) > MAX_MESSAGE_LENGTH:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="mensaje demasiado largo")

    result = await session.execute(select(Battle).where(Battle.id == battle_id))
    battle = result.scalar_one_or_none()
    if battle is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="batalla inexistente")

    if battle.winner_id is None or battle.winner_id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="solo el ganador puede escribir")

    winner = await session.get(User, user_id)
    if winner.is_llm:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="la ia no escribe mensajes")

    if battle.message:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="mensaje ya enviado")

    battle.message = message
    await session.commit()
    await session.refresh(battle)
    return battle


async def get_my_battle(
    session: AsyncSession, user_id: int, date: dt.date
) -> Battle | None:
    result = await session.execute(
        select(Battle).where(
            Battle.battle_date == date,
            (Battle.user_a_id == user_id)
            | (Battle.user_b_id == user_id)
            | (Battle.extra_user_id == user_id),
        )
    )
    return result.scalar_one_or_none()


async def get_battle_players(session: AsyncSession, battle: Battle) -> list[User]:
    user_ids = [battle.user_a_id]
    if battle.user_b_id:
        user_ids.append(battle.user_b_id)
    if battle.extra_user_id:
        user_ids.append(battle.extra_user_id)
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    return list(result.scalars())


async def get_week_battles(
    session: AsyncSession, user_id: int, date: dt.date
) -> list[Battle]:
    monday = date - dt.timedelta(days=date.weekday())
    result = await session.execute(
        select(Battle).where(
            Battle.battle_date >= monday,
            Battle.battle_date <= date,
            (Battle.user_a_id == user_id)
            | (Battle.user_b_id == user_id)
            | (Battle.extra_user_id == user_id),
        ).order_by(Battle.battle_date)
    )
    return list(result.scalars())
