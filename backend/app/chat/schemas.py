from typing import Literal

from pydantic import BaseModel, Field


class MensajeHistorial(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=1000)
    historial: list[MensajeHistorial] = Field(default=[], max_length=20)
