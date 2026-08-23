from pydantic import BaseModel, Field, model_validator


class PredictionRequest(BaseModel):
    event_id: int
    home_score: int | None = Field(default=None, ge=0, le=99)
    away_score: int | None = Field(default=None, ge=0, le=99)
    positions: list[str] | None = Field(default=None, min_length=1, max_length=30)

    @model_validator(mode="after")
    def check_payload_by_shape(self):
        has_scores = self.home_score is not None and self.away_score is not None
        has_positions = self.positions is not None
        if has_scores and has_positions:
            raise ValueError("no se puede enviar marcador y posiciones a la vez")
        if not has_scores and not has_positions:
            raise ValueError("se requiere marcador o posiciones")
        return self


class PredictionOut(BaseModel):
    id: int
    event_id: int
    home_score: int | None
    away_score: int | None
    positions: list[str] | None
