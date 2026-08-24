from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.deps import get_provider, get_session
from app.scoring.service import get_leaderboard, update_results
from app.sports.espn import ESPNProvider

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
async def leaderboard(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    return await get_leaderboard(session)


@router.post("/update")
async def trigger_update(
    session: AsyncSession = Depends(get_session),
    provider: ESPNProvider = Depends(get_provider),
    current_user=Depends(get_current_user),
) -> dict:
    updated = await update_results(session, provider)
    return {"predictions_actualizadas": updated}
