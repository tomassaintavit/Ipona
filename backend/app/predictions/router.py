import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.db.models import Prediction, SportEvent, User
from app.deps import get_session
from app.predictions.schemas import (
    PredictionHistory,
    PredictionOut,
    PredictionRequest,
)
from app.sports.models import EventStatus, Sport

router = APIRouter(prefix="/predictions", tags=["predictions"])

SCORE_SPORTS = {Sport.FOOTBALL.value, Sport.BASKETBALL.value}


@router.post("", response_model=PredictionOut, status_code=201)
async def save_prediction(
    payload: PredictionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PredictionOut:
    event = await session.get(SportEvent, payload.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="evento inexistente")
    if event.start_time_utc <= dt.datetime.now(dt.UTC):
        raise HTTPException(status_code=403, detail="el evento ya comenzo")

    expects_scores = event.sport in SCORE_SPORTS
    sends_scores = payload.home_score is not None
    if expects_scores != sends_scores:
        raise HTTPException(
            status_code=422,
            detail="formato de prediccion invalido para este deporte",
        )
    if not expects_scores and len(payload.positions or []) < 1:
        raise HTTPException(status_code=422, detail="se requiere el orden de pilotos")

    result = await session.execute(
        select(Prediction).where(
            Prediction.user_id == current_user.id,
            Prediction.event_id == event.id,
        )
    )
    prediction = result.scalar_one_or_none()
    if prediction is None:
        prediction = Prediction(user_id=current_user.id, event_id=event.id)
        session.add(prediction)
    prediction.home_score = payload.home_score
    prediction.away_score = payload.away_score
    prediction.positions = payload.positions
    await session.commit()
    await session.refresh(prediction)
    return _to_out(prediction)


@router.get("/my", response_model=list[PredictionOut])
async def my_predictions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[PredictionOut]:
    result = await session.execute(
        select(Prediction).where(Prediction.user_id == current_user.id)
    )
    return [_to_out(p) for p in result.scalars()]


@router.get("/history", response_model=list[PredictionHistory])
async def prediction_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[PredictionHistory]:
    result = await session.execute(
        select(Prediction, SportEvent)
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(
            Prediction.user_id == current_user.id,
            SportEvent.status == EventStatus.FINAL.value,
        )
        .order_by(SportEvent.start_time_utc.desc())
    )
    return [_to_history(p, e) for p, e in result.all()]


def _to_history(prediction: Prediction, event: SportEvent) -> PredictionHistory:
    positions = prediction.positions
    if isinstance(positions, str):
        positions = [positions]
    final_positions = event.final_positions
    if isinstance(final_positions, str):
        final_positions = [final_positions]
    return PredictionHistory(
        id=prediction.id,
        event_id=event.id,
        league=event.league,
        sport=event.sport,
        start_time_utc=event.start_time_utc,
        teams=[t for t in (event.home_team, event.away_team) if t],
        predicted_home=prediction.home_score,
        predicted_away=prediction.away_score,
        predicted_positions=positions,
        final_home=event.final_home_score,
        final_away=event.final_away_score,
        final_positions=final_positions,
        points=float(prediction.points) if prediction.points is not None else None,
    )


def _to_out(prediction: Prediction) -> PredictionOut:
    positions = prediction.positions
    if isinstance(positions, str):
        positions = [positions]
    return PredictionOut(
        id=prediction.id,
        event_id=prediction.event_id,
        home_score=prediction.home_score,
        away_score=prediction.away_score,
        positions=positions,
    )
