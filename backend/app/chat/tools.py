import json

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Prediction, SportEvent, User


async def _find_user(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(
        select(User).where(func.lower(User.username) == username.lower())
    )
    return result.scalar_one_or_none()


def _partido_dict(event: SportEvent) -> dict:
    return {
        "fecha": event.start_time_utc.isoformat(),
        "liga": event.league,
        "local": event.home_team,
        "visitante": event.away_team,
        "marcador": (
            f"{event.final_home_score}-{event.final_away_score}"
            if event.final_home_score is not None
            else None
        ),
    }


async def ultimos_partidos(
    session: AsyncSession, equipo: str, limite: int = 5
) -> list[dict]:
    limite = max(1, min(int(limite), 10))
    result = await session.execute(
        select(SportEvent)
        .where(
            or_(
                func.lower(SportEvent.home_team) == equipo.lower(),
                func.lower(SportEvent.away_team) == equipo.lower(),
            ),
            SportEvent.final_home_score.isnot(None),
        )
        .order_by(SportEvent.start_time_utc.desc())
        .limit(limite)
    )
    partidos = []
    for e in result.scalars():
        d = _partido_dict(e)
        d["condicion"] = "local" if e.home_team and e.home_team.lower() == equipo.lower() else "visitante"
        partidos.append(d)
    return partidos


async def tabla_posiciones(session: AsyncSession) -> list[dict]:
    from app.scoring.service import get_leaderboard

    return await get_leaderboard(session)


async def predicciones_usuario(session: AsyncSession, usuario: str) -> list[dict]:
    user = await _find_user(session, usuario)
    if user is None:
        return {"error": f"usuario '{usuario}' no encontrado"}
    result = await session.execute(
        select(Prediction, SportEvent)
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(Prediction.user_id == user.id)
        .order_by(Prediction.created_at.desc())
        .limit(15)
    )
    out = []
    for pred, event in result.all():
        pronostico = (
            f"{pred.home_score}-{pred.away_score}"
            if pred.home_score is not None
            else (",".join(pred.positions or []) or "?")
        )
        out.append(
            {
                "evento": f"{event.home_team} vs {event.away_team}" if event.home_team else event.league,
                "pronostico": pronostico,
                "puntos": float(pred.points) if pred.points is not None else None,
                "fecha_evento": event.start_time_utc.isoformat(),
            }
        )
    return out


async def proximos_eventos(session: AsyncSession) -> list[dict]:
    import datetime as dt

    result = await session.execute(
        select(SportEvent)
        .where(
            SportEvent.start_time_utc > dt.datetime.now(dt.UTC),
            SportEvent.status == "programado",
        )
        .order_by(SportEvent.start_time_utc.asc())
        .limit(10)
    )
    eventos = []
    for e in result.scalars():
        eventos.append(
            {
                "deporte": e.sport,
                "liga": e.league,
                "enfrentamiento": (
                    f"{e.home_team} vs {e.away_team}"
                    if e.home_team
                    else ", ".join((e.participants or [])[:5])
                ),
                "inicio": e.start_time_utc.isoformat(),
            }
        )
    return eventos


async def precision_usuario(session: AsyncSession, usuario: str) -> dict:
    user = await _find_user(session, usuario)
    if user is None:
        return {"error": f"usuario '{usuario}' no encontrado"}
    result = await session.execute(
        select(
            SportEvent.sport,
            func.count(Prediction.id).label("total"),
            func.sum(func.coalesce(Prediction.points, 0.0)).label("puntos"),
        )
        .join(SportEvent, Prediction.event_id == SportEvent.id)
        .where(Prediction.user_id == user.id)
        .group_by(SportEvent.sport)
    )
    por_deporte = {}
    for sport, total, puntos in result.all():
        por_deporte[sport] = {
            "predicciones": total,
            "puntos": float(puntos or 0.0),
        }
    return {"usuario": user.username, "por_deporte": por_deporte}


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "ultimos_partidos",
            "description": "Devuelve los últimos partidos ya jugados de un equipo, con marcador final.",
            "parameters": {
                "type": "object",
                "properties": {
                    "equipo": {"type": "string", "description": "Nombre del equipo"},
                    "limite": {"type": "integer", "description": "Cantidad máxima (1-10)"},
                },
                "required": ["equipo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tabla_posiciones",
            "description": "Devuelve la tabla de posiciones del juego con puntos por jugador.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "predicciones_usuario",
            "description": "Devuelve las últimas predicciones de un jugador del juego.",
            "parameters": {
                "type": "object",
                "properties": {"usuario": {"type": "string", "description": "Nombre de usuario"}},
                "required": ["usuario"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "proximos_eventos",
            "description": "Devuelve los próximos eventos deportivos disponibles para predecir.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "precision_usuario",
            "description": "Devuelve la precisión y puntos de un jugador agrupados por deporte.",
            "parameters": {
                "type": "object",
                "properties": {"usuario": {"type": "string"}},
                "required": ["usuario"],
            },
        },
    },
]

HERRAMIENTAS = {
    "ultimos_partidos": ultimos_partidos,
    "tabla_posiciones": tabla_posiciones,
    "predicciones_usuario": predicciones_usuario,
    "proximos_eventos": proximos_eventos,
    "precision_usuario": precision_usuario,
}
