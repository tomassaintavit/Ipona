import datetime as dt

import httpx

from app.sports.models import EventResult, EventStatus, Sport, SportEvent
from app.sports.provider import SportsDataProvider

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

SPORT_PATHS: dict[Sport, list[str]] = {
    Sport.FOOTBALL: [
        "soccer/arg.1",
        "soccer/conmebol.libertadores",
        "soccer/conmebol.sudamericana",
        "soccer/eng.1",
        "soccer/esp.1",
        "soccer/ita.1",
        "soccer/uefa.champions",
    ],
    Sport.BASKETBALL: ["basketball/nba"],
    Sport.F1: ["racing/f1"],
}

_STATE_TO_STATUS = {
    "pre": EventStatus.SCHEDULED,
    "in": EventStatus.IN_PROGRESS,
    "post": EventStatus.FINAL,
}


class ESPNProvider(SportsDataProvider):
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client or httpx.AsyncClient(base_url=BASE_URL)

    async def get_day_events(self, date: dt.date, sport: Sport) -> list[SportEvent]:
        events: list[SportEvent] = []
        for path in SPORT_PATHS[sport]:
            data = await self._fetch_scoreboard(path, date)
            if data is None:
                continue
            league = _league_name(data)
            for raw in data.get("events", []):
                events.append(_parse_event(raw, sport, league))
        return events

    async def get_event_result(self, event: SportEvent) -> EventResult:
        date = event.start_time_utc.date()
        fechas = [date, date - dt.timedelta(days=1), date + dt.timedelta(days=1)]
        for fecha in fechas:
            for path in SPORT_PATHS[event.sport]:
                data = await self._fetch_scoreboard(path, fecha)
                if data is None:
                    continue
                for raw in data.get("events", []):
                    if raw.get("id") == event.id:
                        return _parse_result(raw, event)
        raise LookupError(f"evento {event.id} no encontrado en ESPN")

    async def _fetch_scoreboard(self, path: str, date: dt.date) -> dict | None:
        response = await self._client.get(
            f"/{path}/scoreboard", params={"dates": date.strftime("%Y%m%d")}
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


def _league_name(data: dict) -> str:
    leagues = data.get("leagues") or [{}]
    return leagues[0].get("name", "")


def _parse_event(raw: dict, sport: Sport, league: str) -> SportEvent:
    competition = raw["competitions"][0]
    competitors = competition.get("competitors", [])
    home = next((c for c in competitors if c.get("homeAway") == "home"), None)
    away = next((c for c in competitors if c.get("homeAway") == "away"), None)
    state = raw["status"]["type"]["state"]
    return SportEvent(
        id=str(raw["id"]),
        sport=sport,
        league=league,
        start_time_utc=dt.datetime.fromisoformat(raw["date"].replace("Z", "+00:00")),
        status=_STATE_TO_STATUS[state],
        home_team=_team_name(home),
        away_team=_team_name(away),
        participants=[_athlete_name(c) for c in competitors],
        favorito=_favorito(competition, competitors),
    )


def _favorito(competition: dict, competitors: list[dict]) -> str | None:
    odds = next((o for o in competition.get("odds") or [] if o), None)
    if not odds:
        return None
    moneyline = odds.get("moneyline") or {}

    def _valor(side: str) -> int | None:
        try:
            return int(((moneyline.get(side) or {}).get("close") or {}).get("odds"))
        except (TypeError, ValueError):
            return None

    local, visitante = _valor("home"), _valor("away")
    home_c = next((c for c in competitors if c.get("homeAway") == "home"), None)
    away_c = next((c for c in competitors if c.get("homeAway") == "away"), None)

    if local is not None and (visitante is None or local < visitante):
        return _team_name(home_c)
    if visitante is not None:
        return _team_name(away_c)

    detalles = (odds.get("details") or "").split(" ")[0].strip()
    if detalles:
        for c in competitors:
            equipo = c.get("team") or {}
            if (equipo.get("abbreviation") or "").upper() == detalles.upper():
                return equipo.get("displayName")
    return None


def _parse_result(raw: dict, event: SportEvent) -> EventResult:
    competition = raw["competitions"][0]
    competitors = competition.get("competitors", [])
    completed = bool(raw["status"]["type"].get("completed"))
    result = EventResult(event_id=event.id, completed=completed)
    if event.sport is Sport.F1:
        ordered = sorted(competitors, key=lambda c: c.get("order", 0))
        result.positions = [_athlete_name(c) for c in ordered]
    else:
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        result.home_score = _to_score(home)
        result.away_score = _to_score(away)
    return result


def _team_name(competitor: dict | None) -> str | None:
    if not competitor:
        return None
    return competitor.get("team", {}).get("displayName")


def _athlete_name(competitor: dict) -> str:
    athlete = competitor.get("athlete") or {}
    return athlete.get("displayName") or competitor.get("team", {}).get("displayName", "")


def _to_score(competitor: dict | None) -> int | None:
    if not competitor or competitor.get("score") in (None, ""):
        return None
    return int(float(competitor["score"]))
