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


async def get_leaderboard(session: AsyncSession) -> list[dict]:
    result = await session.execute(
        select(
            User.id,
            User.username,
            User.is_llm,
            func.coalesce(func.sum(Prediction.points), 0.0).label("total"),
            func.count(Prediction.id).label("predictions"),
        )
        .outerjoin(Prediction, Prediction.user_id == User.id)
        .group_by(User.id, User.username, User.is_llm)
        .order_by(func.sum(Prediction.points).desc())
    )
    rows = result.all()
    ranked = []
    for position, (user_id, username, is_llm, total, count) in enumerate(rows, start=1):
        ranked.append(
            {
                "position": position,
                "username": username,
                "is_llm": is_llm,
                "total_points": float(total),
                "predictions": count,
            }
        )
    return ranked
