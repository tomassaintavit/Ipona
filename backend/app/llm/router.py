from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.models import User
from app.deps import get_session
from app.llm.client import LLMClient
from app.llm.player import predict_day_events

router = APIRouter(prefix="/llm", tags=["llm"])


def get_llm_client() -> LLMClient:
    return LLMClient()


@router.post("/predict")
@limiter.limit(get_settings().llm_rate_limit)
async def trigger_predictions(
    request: Request,
    session: AsyncSession = Depends(get_session),
    client: LLMClient = Depends(get_llm_client),
    current_user: User = Depends(get_current_user),
) -> dict:
    saved = await predict_day_events(session, client)
    return {"predicciones_generadas": len(saved)}
