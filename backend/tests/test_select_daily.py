import datetime as dt

from app.events.service import select_daily_events
from app.db.models import SportEvent


NOW = dt.datetime(2026, 8, 23, 12, 0, tzinfo=dt.UTC)


def make_event(id, league, hours_from_now, status="programado"):
    return SportEvent(
        id=id,
        provider="espn",
        provider_event_id=str(id),
        sport="futbol",
        league=league,
        start_time_utc=NOW + dt.timedelta(hours=hours_from_now),
        status=status,
        home_team="A",
        away_team="B",
    )


def test_selects_max_six_events():
    leagues = ["Liga A", "Liga B", "Liga C", "Liga D"]
    events = [
        make_event(i * 5 + j, leagues[i], 1 + i) for i in range(4) for j in range(5)
    ]

    selected = select_daily_events(events, now=NOW)

    assert len(selected) == 6


def test_respects_league_diversity_cap():
    events = (
        [make_event(i, "Liga A", 1 + i) for i in range(5)]
        + [make_event(100 + i, "Liga B", 1 + i) for i in range(5)]
    )

    selected = select_daily_events(events, now=NOW, min_events=2)

    counts = {}
    for e in selected:
        counts[e.league] = counts.get(e.league, 0) + 1
    assert all(c <= 3 for c in counts.values())


def test_excludes_past_and_non_scheduled_events():
    events = [
        make_event(1, "Liga A", -2),
        make_event(2, "Liga A", 1, status="finalizado"),
        make_event(3, "Liga B", 3),
    ]

    selected = select_daily_events(events, now=NOW, min_events=2)

    assert [e.id for e in selected] == [3]


def test_fills_minimum_when_diversity_limits_leave_gaps():
    events = [make_event(i, f"Liga {i}", 1 + i) for i in range(4)]

    selected = select_daily_events(
        events, now=NOW, max_events=10, min_events=2, max_per_league=3
    )

    assert len(selected) == 4


def test_orders_by_start_time():
    events = [
        make_event(1, "Liga A", 5),
        make_event(2, "Liga B", 2),
        make_event(3, "Liga C", 8),
    ]

    selected = select_daily_events(events, now=NOW, min_events=2)

    assert [e.id for e in selected] == [2, 1, 3]
