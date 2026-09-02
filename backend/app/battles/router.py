import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.battles.schemas import BattleMessageRequest, BattleOut, RecentBattleOut
from app.battles.service import get_my_battle, get_week_battles, set_battle_message
from app.db.models import User
from app.deps import get_session

router = APIRouter(prefix="/battles", tags=["battles"])


@router.get("/today", response_model=BattleOut | None)
async def today_battle(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BattleOut | None:
    battle = await get_my_battle(session, current_user.id, dt.datetime.now(dt.UTC).date())
    if battle is None:
        return None
    return await _serialize_my_battle(session, battle, current_user.id)


@router.get("/week", response_model=list[RecentBattleOut])
async def week_battles(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[RecentBattleOut]:
    battles = await get_week_battles(
        session, current_user.id, dt.datetime.now(dt.UTC).date()
    )
    return [await _serialize_recent(session, b, current_user.id) for b in battles]


@router.post("/message", response_model=BattleOut)
async def send_message(
    payload: BattleMessageRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BattleOut:
    battle = await set_battle_message(session, payload.battle_id, current_user.id, payload.message)
    return await _serialize_my_battle(session, battle, current_user.id)


async def _opponent_of(session, battle, user_id: int) -> tuple[User | None, bool]:
    from app.battles.service import get_battle_players

    players = await get_battle_players(session, battle)
    others = [p for p in players if p.id != user_id]
    opponent = others[0] if others else players[0]
    return opponent, len(players) > 2


async def _serialize_my_battle(session, battle, user_id: int) -> BattleOut:
    opponent, is_trio = await _opponent_of(session, battle, user_id)

    from app.battles.service import _day_points

    my_points = await _day_points(session, user_id, battle.battle_date)
    opp_points = await _day_points(session, opponent.id, battle.battle_date)

    winner = None
    if battle.winner_id is not None:
        winner = "me" if battle.winner_id == user_id else "opponent"

    return BattleOut(
        battle_id=battle.id,
        battle_date=battle.battle_date.isoformat(),
        opponent={
            "username": opponent.username,
            "is_llm": opponent.is_llm,
        },
        is_trio=is_trio,
        my_points=my_points,
        opponent_points=opp_points,
        status=battle.status,
        winner=winner,
        winner_message=battle.message,
    )


async def _serialize_recent(session, battle, user_id: int) -> RecentBattleOut:
    opponent, _ = await _opponent_of(session, battle, user_id)
    from app.battles.service import _day_points

    my_points = await _day_points(session, user_id, battle.battle_date)
    opp_points = await _day_points(session, opponent.id, battle.battle_date)

    result = None
    if battle.status == "resuelta":
        if battle.winner_id is None:
            result = "empate"
        elif battle.winner_id == user_id:
            result = "gane"
        else:
            result = "perdi"

    return RecentBattleOut(
        battle_date=battle.battle_date.isoformat(),
        opponent={
            "username": opponent.username,
            "is_llm": opponent.is_llm,
        },
        result=result,
        my_points=my_points,
        opponent_points=opp_points,
        winner_message=battle.message if battle.winner_id != user_id else None,
    )
