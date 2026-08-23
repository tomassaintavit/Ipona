import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SportEvent
from app.deps import get_provider, get_session
from app.events.service import select_daily_events, sync_day_events
from app.sports.espn import ESPNProvider

router = APIRouter()


@router.get("/events/today")
async def today_events(
    session: AsyncSession = Depends(get_session),
    provider: ESPNProvider = Depends(get_provider),
) -> list[dict]:
    today = dt.datetime.now(dt.UTC).date()
    await sync_day_events(session, provider, today)

    result = await session.execute(
        select(SportEvent).where(
            SportEvent.start_time_utc
            >= dt.datetime.combine(today, dt.time.min, tzinfo=dt.UTC),
            SportEvent.start_time_utc
            <= dt.datetime.combine(today, dt.time.max, tzinfo=dt.UTC),
        )
    )
    curated = select_daily_events(list(result.scalars()))
    return [_serialize(e) for e in curated]


def _serialize(event: SportEvent) -> dict:
    return {
        "id": event.id,
        "provider_event_id": event.provider_event_id,
        "sport": event.sport,
        "league": event.league,
        "start_time_utc": event.start_time_utc.isoformat(),
        "status": event.status,
        "home_team": event.home_team,
        "away_team": event.away_team,
        "participants": event.participants,
    }
