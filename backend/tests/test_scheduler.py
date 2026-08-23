import datetime
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from app import scheduler as scheduler_module
from app.scheduler import configure_scheduler, shutdown_scheduler, start_scheduler


@pytest.fixture(autouse=True)
def isolate_scheduler(monkeypatch):
    shutdown_scheduler()
    for name in ("job_sync_events", "job_llm_predictions", "job_update_results"):
        monkeypatch.setattr(scheduler_module, name, AsyncMock(return_value=None))
    yield
    shutdown_scheduler()
    scheduler_module.get_settings.cache_clear()


def test_registra_los_tres_jobs():
    sched = configure_scheduler()

    jobs = {job.id: job for job in sched.get_jobs()}

    assert set(jobs) == {"sync_events", "llm_predictions", "update_results"}
    assert str(jobs["sync_events"].trigger) == "cron[hour='6', minute='0']"
    assert "minute='15'" in str(jobs["llm_predictions"].trigger)
    assert jobs["update_results"].trigger.interval == timedelta(hours=1)


def test_start_respeta_configuracion(monkeypatch):
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    scheduler_module.get_settings.cache_clear()

    started = start_scheduler()

    assert started is False
    assert not scheduler_module.scheduler.running
    scheduler_module.get_settings.cache_clear()


async def test_start_inicia_el_scheduler(monkeypatch):
    monkeypatch.setenv("SCHEDULER_ENABLED", "true")
    scheduler_module.get_settings.cache_clear()

    started = start_scheduler()

    assert started is True
    assert scheduler_module.scheduler.running
