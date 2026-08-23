import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.db.engine import create_engine, create_session_factory
from app.events.service import sync_day_events
from app.llm.client import LLMClient
from app.llm.player import predict_day_events
from app.sports.espn import ESPNProvider

logger = logging.getLogger(__name__)

_engine = None
_session_factory = None


def _get_session_factory():
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_engine()
        _session_factory = create_session_factory(_engine)
    return _session_factory


async def job_sync_events():
    import datetime as dt

    factory = _get_session_factory()
    async with factory() as session:
        events = await sync_day_events(session, ESPNProvider(), dt.datetime.now(dt.UTC).date())
        logger.info("eventos sincronizados: %s", len(events))


async def job_llm_predictions():
    factory = _get_session_factory()
    async with factory() as session:
        saved = await predict_day_events(session, LLMClient())
        logger.info("predicciones del llm generadas: %s", len(saved))


async def job_update_results():
    from app.scoring.service import update_results

    factory = _get_session_factory()
    async with factory() as session:
        updated = await update_results(session, ESPNProvider())
        logger.info("predicciones puntuadas: %s", updated)


scheduler = AsyncIOScheduler(timezone="UTC")


def configure_scheduler() -> AsyncIOScheduler:
    scheduler.add_job(
        job_sync_events, "cron", hour=6, minute=0, id="sync_events", replace_existing=True
    )
    scheduler.add_job(
        job_llm_predictions,
        "cron",
        hour=6,
        minute=15,
        id="llm_predictions",
        replace_existing=True,
    )
    scheduler.add_job(
        job_update_results,
        "interval",
        hours=1,
        id="update_results",
        replace_existing=True,
    )
    return scheduler


def start_scheduler() -> bool:
    if not get_settings().scheduler_enabled:
        logger.info("scheduler deshabilitado por configuracion")
        return False
    configure_scheduler()
    scheduler.start()
    return True


def shutdown_scheduler() -> None:
    if not scheduler.running:
        return
    try:
        scheduler.shutdown(wait=False)
    except RuntimeError:
        logger.warning("scheduler apagado sin event loop activo")
