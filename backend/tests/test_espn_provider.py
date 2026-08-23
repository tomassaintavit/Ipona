import datetime as dt

import httpx
import pytest

from app.sports.espn import BASE_URL, ESPNProvider
from app.sports.models import EventStatus, Sport


def _odds_moneyline(home_odds, away_odds):
    return {
        "provider": {"name": "DraftKings"},
        "moneyline": {
            "home": {"close": {"odds": home_odds}},
            "away": {"close": {"odds": away_odds}},
        },
    }


def _soccer_scoreboard(event_id, state, completed, home_score=None, away_score=None, odds=None):
    return {
        "leagues": [{"name": "Argentine Liga Profesional de Fútbol"}],
        "events": [
            {
                "id": event_id,
                "date": "2026-08-23T17:45Z",
                "status": {"type": {"state": state, "completed": completed}},
                "competitions": [
                    {
                        "competitors": [
                            {
                                "homeAway": "home",
                                "team": {"displayName": "Barracas Central", "abbreviation": "BAR"},
                                "score": home_score,
                            },
                            {
                                "homeAway": "away",
                                "team": {"displayName": "Platense", "abbreviation": "PLA"},
                                "score": away_score,
                            },
                        ],
                        **({"odds": [odds]} if odds else {}),
                    }
                ],
            }
        ],
    }


def _f1_scoreboard():
    return {
        "leagues": [{"name": "Formula 1"}],
        "events": [
            {
                "id": "600057441",
                "date": "2026-08-23T10:30Z",
                "status": {"type": {"state": "post", "completed": True}},
                "competitions": [
                    {
                        "competitors": [
                            {"order": 2, "athlete": {"displayName": "Lando Norris"}},
                            {"order": 1, "athlete": {"displayName": "Kimi Antonelli"}},
                            {"order": 3, "athlete": {"displayName": "George Russell"}},
                        ]
                    }
                ],
            }
        ],
    }


def make_client(routes):
    def handler(request: httpx.Request) -> httpx.Response:
        for suffix, payload in routes.items():
            if request.url.path.endswith(suffix):
                return httpx.Response(200, json=payload)
        return httpx.Response(404)

    return httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url=BASE_URL
    )


async def test_get_day_events_parses_soccer_match():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard("1", "pre", False),
    }
    provider = ESPNProvider(client=make_client(routes))

    events = await provider.get_day_events(dt.date(2026, 8, 23), Sport.FOOTBALL)

    assert len(events) == 1
    event = events[0]
    assert event.id == "1"
    assert event.home_team == "Barracas Central"
    assert event.away_team == "Platense"
    assert event.status is EventStatus.SCHEDULED
    assert event.start_time_utc == dt.datetime(2026, 8, 23, 17, 45, tzinfo=dt.UTC)
    assert event.favorito is None


async def test_detecta_favorito_por_moneyline():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard(
            "1", "pre", False, odds=_odds_moneyline("-180", "+150")
        ),
    }
    provider = ESPNProvider(client=make_client(routes))

    events = await provider.get_day_events(dt.date(2026, 8, 23), Sport.FOOTBALL)

    assert events[0].favorito == "Barracas Central"


async def test_favorito_visitante_cuando_su_cuota_gana():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard(
            "2", "pre", False, odds=_odds_moneyline("+200", "-150")
        ),
    }
    provider = ESPNProvider(client=make_client(routes))

    events = await provider.get_day_events(dt.date(2026, 8, 23), Sport.FOOTBALL)

    assert events[0].favorito == "Platense"


async def test_favorito_sin_moneyline_usa_details_con_abreviatura():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard(
            "3",
            "pre",
            False,
            odds={"provider": {"name": "DraftKings"}, "details": "PLA -140"},
        ),
    }
    provider = ESPNProvider(client=make_client(routes))

    events = await provider.get_day_events(dt.date(2026, 8, 23), Sport.FOOTBALL)

    assert events[0].favorito == "Platense"


async def test_get_day_events_queries_all_football_leagues():
    def routes_with_two_leagues(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/arg.1/scoreboard"):
            return httpx.Response(200, json=_soccer_scoreboard("1", "pre", False))
        return httpx.Response(200, json={"leagues": [], "events": []})

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(routes_with_two_leagues), base_url=BASE_URL
    )
    provider = ESPNProvider(client=client)

    events = await provider.get_day_events(dt.date(2026, 8, 23), Sport.FOOTBALL)

    assert len(events) == 1


async def test_get_event_result_scores_for_final_match():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard("9", "post", True, 2, 1),
    }
    provider = ESPNProvider(client=make_client(routes))
    from app.sports.models import SportEvent

    event = SportEvent(
        id="9",
        sport=Sport.FOOTBALL,
        league="Liga",
        start_time_utc=dt.datetime(2026, 8, 23, 17, 45, tzinfo=dt.UTC),
        status=EventStatus.FINAL,
        home_team="A",
        away_team="B",
    )

    result = await provider.get_event_result(event)

    assert result.completed is True
    assert result.home_score == 2
    assert result.away_score == 1
    assert result.positions is None


async def test_get_event_result_positions_for_f1_race():
    routes = {"/racing/f1/scoreboard": _f1_scoreboard()}
    provider = ESPNProvider(client=make_client(routes))
    from app.sports.models import SportEvent

    event = SportEvent(
        id="600057441",
        sport=Sport.F1,
        league="Formula 1",
        start_time_utc=dt.datetime(2026, 8, 23, 10, 30, tzinfo=dt.UTC),
        status=EventStatus.FINAL,
    )

    result = await provider.get_event_result(event)

    assert result.completed is True
    assert result.positions[0] == "Kimi Antonelli"
    assert result.positions[2] == "George Russell"


async def test_get_event_result_raises_when_not_found():
    routes = {
        "/soccer/arg.1/scoreboard": _soccer_scoreboard("999", "post", True, 1, 0),
    }
    provider = ESPNProvider(client=make_client(routes))
    from app.sports.models import SportEvent

    event = SportEvent(
        id="404",
        sport=Sport.FOOTBALL,
        league="Liga",
        start_time_utc=dt.datetime(2026, 8, 23, 17, 45, tzinfo=dt.UTC),
        status=EventStatus.FINAL,
    )

    with pytest.raises(LookupError):
        await provider.get_event_result(event)
