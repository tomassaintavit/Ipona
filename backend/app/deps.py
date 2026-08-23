from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import create_engine, create_session_factory
from app.sports.espn import ESPNProvider

_engine = None
_session_factory = None


async def get_session() -> AsyncIterator[AsyncSession]:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_engine()
        _session_factory = create_session_factory(_engine)
    async with _session_factory() as session:
        yield session


def get_provider() -> ESPNProvider:
    return ESPNProvider()
