from pydantic import BaseModel, Field


class OpponentOut(BaseModel):
    username: str
    is_llm: bool


class BattleOut(BaseModel):
    battle_id: int
    battle_date: str
    opponent: OpponentOut
    is_trio: bool
    my_points: float | None = None
    opponent_points: float | None = None
    status: str
    winner: str | None = None
    winner_message: str | None = None


class RecentBattleOut(BaseModel):
    battle_date: str
    opponent: OpponentOut
    result: str | None = None
    my_points: float | None = None
    opponent_points: float | None = None
    winner_message: str | None = None


class BattleMessageRequest(BaseModel):
    battle_id: int
    message: str = Field(..., min_length=1, max_length=100)
