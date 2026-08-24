from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.db.models import LLMCall, Prediction, SportEvent, User
from app.deps import get_session
from app.llm.player import LLM_USERNAME

router = APIRouter(prefix="/stats", tags=["stats"])


async def _accuracy_by_sport(session: AsyncSession, user_id: int) -> list[dict]:
    result = await session.execute(
        select(
            SportEvent.sport,
            func.count(Prediction.id).label("total"),
            func.sum(
                case((Prediction.points >= 1.0, 1), else_=0)
            ).label("aciertos"),
            func.sum(case((Prediction.points == 3.0, 1), else_=0)).label("exactos"),
            func.coalesce(func.sum(Prediction.points), 0.0).label("puntos"),
        )
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(Prediction.user_id == user_id)
        .group_by(SportEvent.sport)
    )
    rows = result.all()
    stats = []
    for sport, total, aciertos, exactos, puntos in sorted(rows):
        total = total or 0
        aciertos = aciertos or 0
        exactos = exactos or 0
        stats.append(
            {
                "sport": sport,
                "predicciones": total,
                "aciertos": int(aciertos),
                "marcadores_exactos": int(exactos),
                "precision": round(float(aciertos) / total, 3) if total else 0.0,
                "puntos": float(puntos),
            }
        )
    return stats


@router.get("/me")
async def my_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    by_sport = await _accuracy_by_sport(session, current_user.id)
    total = sum(s["predicciones"] for s in by_sport)
    aciertos = sum(s["aciertos"] for s in by_sport)
    return {
        "username": current_user.username,
        "predicciones": total,
        "aciertos": aciertos,
        "precision": round(aciertos / total, 3) if total else 0.0,
        "por_deporte": by_sport,
    }


@router.get("/llm")
async def llm_stats(session: AsyncSession = Depends(get_session)) -> dict:
    user_result = await session.execute(select(User).where(User.username == LLM_USERNAME))
    llm_user = user_result.scalar_one_or_none()
    if llm_user is None:
        return {"predicciones": 0, "precision": 0.0, "por_deporte": [], "tokens": {}}
    by_sport = await _accuracy_by_sport(session, llm_user.id)
    tokens_result = await session.execute(
        select(
            func.coalesce(func.sum(LLMCall.prompt_tokens), 0),
            func.coalesce(func.sum(LLMCall.completion_tokens), 0),
            func.coalesce(func.sum(LLMCall.total_tokens), 0),
            func.count(LLMCall.id),
        )
    )
    prompt_t, completion_t, total_t, llamadas = tokens_result.one()
    total = sum(s["predicciones"] for s in by_sport)
    aciertos = sum(s["aciertos"] for s in by_sport)
    return {
        "username": llm_user.username,
        "predicciones": total,
        "aciertos": aciertos,
        "precision": round(aciertos / total, 3) if total else 0.0,
        "por_deporte": by_sport,
        "tokens": {
            "llamadas": llamadas,
            "prompt": int(prompt_t),
            "completion": int(completion_t),
            "total": int(total_t),
        },
    }
