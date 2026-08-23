import datetime as dt
from enum import StrEnum

from pydantic import BaseModel


class Sport(StrEnum):
    FOOTBALL = "futbol"
    BASKETBALL = "basquet"
    F1 = "formula_1"


class EventStatus(StrEnum):
    SCHEDULED = "programado"
    IN_PROGRESS = "en_curso"
    FINAL = "finalizado"


class SportEvent(BaseModel):
    id: str
    sport: Sport
    league: str
    start_time_utc: dt.datetime
    status: EventStatus
    home_team: str | None = None
    away_team: str | None = None
    participants: list[str] = []
    favorito: str | None = None


class EventResult(BaseModel):
    event_id: str
    completed: bool
    home_score: int | None = None
    away_score: int | None = None
    positions: list[str] | None = None
