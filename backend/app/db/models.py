import datetime as dt

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_llm: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )


class SportEvent(Base):
    __tablename__ = "sport_events"
    __table_args__ = (UniqueConstraint("provider", "provider_event_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(30), default="espn")
    provider_event_id: Mapped[str] = mapped_column(String(50))
    sport: Mapped[str] = mapped_column(String(20))
    league: Mapped[str] = mapped_column(String(100))
    start_time_utc: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))
    home_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    away_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    participants: Mapped[list | None] = mapped_column(JSON, nullable=True)
    final_home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_positions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    favorito: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Prediction(Base):
    __tablename__ = "predictions"
    __table_args__ = (UniqueConstraint("user_id", "event_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("sport_events.id"))
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    positions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    points: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )


class LLMCall(Base):
    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(80))
    prompt_tokens: Mapped[int] = mapped_column(Integer)
    completion_tokens: Mapped[int] = mapped_column(Integer)
    total_tokens: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )


class Battle(Base):
    __tablename__ = "battles"

    id: Mapped[int] = mapped_column(primary_key=True)
    battle_date: Mapped[dt.date] = mapped_column(Date)
    user_a_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_b_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    extra_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pendiente")
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    message: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )
