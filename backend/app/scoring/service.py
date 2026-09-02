import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Prediction, SportEvent, User
from app.scoring.points import compute_points
from app.sports.models import EventResult, EventStatus, SportEvent as DomainEvent
from app.sports.provider import SportsDataProvider


async def update_results(
    session: AsyncSession,
    provider: SportsDataProvider,
) -> int:
    result = await session.execute(
        select(Prediction, SportEvent)
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(
            Prediction.points.is_(None),
            SportEvent.start_time_utc < dt.datetime.now(dt.UTC),
        )
    )
    updated = 0
    cache: dict[int, EventResult] = {}
    for prediction, event in result.all():
        if event.id not in cache:
            domain_event = _to_domain(event)
            try:
                provider_result = await provider.get_event_result(domain_event)
            except LookupError:
                continue
            cache[event.id] = provider_result
        provider_result = cache[event.id]
        if not provider_result.completed:
            continue
        _apply_result(event, provider_result)
        points = compute_points(event, prediction)
        prediction.points = points
        updated += 1
    await session.commit()
    return updated


def _apply_result(event: SportEvent, provider_result: EventResult) -> None:
    event.final_home_score = provider_result.home_score
    event.final_away_score = provider_result.away_score
    event.final_positions = provider_result.positions
    if provider_result.completed:
        event.status = EventStatus.FINAL.value


def _to_domain(event: SportEvent) -> DomainEvent:
    from app.sports.models import EventStatus, Sport

    return DomainEvent(
        id=event.provider_event_id,
        sport=Sport(event.sport),
        league=event.league,
        start_time_utc=event.start_time_utc,
        status=EventStatus(event.status),
        home_team=event.home_team,
        away_team=event.away_team,
        participants=event.participants or [],
    )


async def get_leaderboard(session: AsyncSession, period: str = "global") -> list[dict]:
    conditions = [_period_condition(period)]
    rows = (
        await session.execute(
            select(
                User.id,
                User.username,
                User.is_llm,
                SportEvent.sport,
                func.coalesce(func.sum(Prediction.points), 0.0),
                func.count(Prediction.id),
            )
            .outerjoin(Prediction, Prediction.user_id == User.id)
            .outerjoin(SportEvent, Prediction.event_id == SportEvent.id)
            .where(*conditions)
            .group_by(User.id, User.username, User.is_llm, SportEvent.sport)
            .order_by(User.id)
        )
    ).all()

    por_usuario: dict[int, dict] = {}
    totales: dict[int, float] = {}
    conteos: dict[int, int] = {}
    for user_id, username, is_llm, sport, puntos, conteo in rows:
        d = por_usuario.setdefault(user_id, {"username": username, "is_llm": is_llm, "sports": {}})
        if sport:
            d["sports"][sport] = float(puntos)
            totales[user_id] = totales.get(user_id, 0.0) + float(puntos)
            conteos[user_id] = conteos.get(user_id, 0) + conteo

    ranked = []
    for pos, (user_id, d) in enumerate(
        sorted(por_usuario.items(), key=lambda kv: -totales.get(kv[0], 0.0)), start=1
    ):
        ranked.append(
            {
                "position": pos,
                "username": d["username"],
                "is_llm": d["is_llm"],
                "total_points": totales.get(user_id, 0.0),
                "predictions": conteos.get(user_id, 0),
                "puntos_por_deporte": d["sports"],
            }
        )
    return ranked


def _period_condition(period: str):
    now = dt.datetime.now(dt.UTC)
    if period == "weekly":
        start = now - dt.timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        return SportEvent.start_time_utc >= start
    if period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return SportEvent.start_time_utc >= start
    return True
