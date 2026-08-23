import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SportEvent
from app.sports.models import EventStatus, Sport, SportEvent as DomainEvent
from app.sports.provider import SportsDataProvider

MAX_DAILY_EVENTS = 10
MIN_DAILY_EVENTS = 2
MAX_PER_LEAGUE = 3


async def sync_day_events(
    session: AsyncSession,
    provider: SportsDataProvider,
    date: dt.date,
) -> list[SportEvent]:
    stored: list[SportEvent] = []
    for sport in Sport:
        domain_events = await provider.get_day_events(date, sport)
        for domain_event in domain_events:
            stored.append(await _upsert_event(session, domain_event))
    await session.commit()
    return stored


async def _upsert_event(session: AsyncSession, domain_event: DomainEvent) -> SportEvent:
    result = await session.execute(
        select(SportEvent).where(
            SportEvent.provider == "espn",
            SportEvent.provider_event_id == domain_event.id,
        )
    )
    db_event = result.scalar_one_or_none()
    if db_event is None:
        db_event = SportEvent(provider="espn", provider_event_id=domain_event.id)
        session.add(db_event)
    db_event.sport = domain_event.sport.value
    db_event.league = domain_event.league
    db_event.start_time_utc = domain_event.start_time_utc
    db_event.status = domain_event.status.value
    db_event.home_team = domain_event.home_team
    db_event.away_team = domain_event.away_team
    db_event.participants = domain_event.participants or None
    return db_event


def select_daily_events(
    events: list[SportEvent],
    now: dt.datetime | None = None,
    max_events: int = MAX_DAILY_EVENTS,
    min_events: int = MIN_DAILY_EVENTS,
    max_per_league: int = MAX_PER_LEAGUE,
) -> list[SportEvent]:
    now = now or dt.datetime.now(dt.UTC)
    upcoming = [
        e for e in events if e.status == EventStatus.SCHEDULED.value and e.start_time_utc > now
    ]
    upcoming.sort(key=lambda e: e.start_time_utc)

    selected: list[SportEvent] = []
    per_league: dict[str, int] = {}
    for event in upcoming:
        if len(selected) >= max_events:
            break
        if per_league.get(event.league, 0) >= max_per_league:
            continue
        selected.append(event)
        per_league[event.league] = per_league.get(event.league, 0) + 1

    if len(selected) < min_events:
        remaining = [e for e in upcoming if e not in selected]
        selected.extend(remaining[: min_events - len(selected)])
    return selected
