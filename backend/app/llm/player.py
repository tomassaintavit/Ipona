import datetime as dt
import json

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Prediction, SportEvent, User
from app.llm.client import LLMClient

LLM_USERNAME = "Cris el pulpo Paul"
LLM_EMAIL = "cris@ipona.ar"
LLM_PASSWORD_HASH = "no-login"


async def ensure_llm_user(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == LLM_USERNAME))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=LLM_EMAIL,
            username=LLM_USERNAME,
            password_hash=LLM_PASSWORD_HASH,
            is_llm=True,
        )
        session.add(user)
        await session.commit()
    return user


async def build_context(session: AsyncSession, events: list[SportEvent]) -> str:
    lines = []
    for event in events:
        context = {"evento_id": event.id}
        for team in _teams(event):
            form = await _team_form(session, team)
            context[team] = form
        if event.favorito:
            context["favorito_casas_de_apuestas"] = event.favorito
        lines.append(json.dumps(context, ensure_ascii=False))
    return "\n".join(lines)


def _teams(event: SportEvent) -> list[str]:
    return [t for t in (event.home_team, event.away_team) if t]


async def _team_form(session: AsyncSession, team: str) -> list[dict]:
    result = await session.execute(
        select(SportEvent)
        .where(
            or_(SportEvent.home_team == team, SportEvent.away_team == team),
            SportEvent.final_home_score.isnot(None),
        )
        .order_by(SportEvent.start_time_utc.desc())
        .limit(5)
    )
    matches = result.scalars().all()
    return [
        {
            "rival": m.away_team if m.home_team == team else m.home_team,
            "marcador": f"{m.final_home_score}-{m.final_away_score}",
            "local": m.home_team == team,
        }
        for m in matches
    ]


SYSTEM_PROMPT = (
    "Sos Cris el pulpo Paul, un pulpo adivino que compite como jugador en un juego "
    "de predicciones deportivas. "
    "Recibis un contexto con eventos proximos y estadisticas recientes de los equipos. "
    "Cuando aparezca 'favorito_casas_de_apuestas', es el equipo que las casas de "
    "apuestas consideran favorito segun dinero apostado: usalo como senal adicional, "
    "no como verdad absoluta. "
    "Devolves SIEMPRE un objeto JSON con la clave 'predicciones', una lista donde cada "
    "elemento tiene 'event_id' y para futbol/basquet 'home_score' y 'away_score' "
    "(enteros >= 0), o para formula_1 'positions' (lista con los 3 pilotos del podio "
    "en orden). No incluyas texto fuera del JSON."
)


async def predict_day_events(session: AsyncSession, client: LLMClient) -> list[Prediction]:
    llm_user = await ensure_llm_user(session)

    now = dt.datetime.now(dt.UTC)
    result = await session.execute(
        select(SportEvent).where(
            SportEvent.start_time_utc > now,
            SportEvent.status == "programado",
        )
    )
    upcoming = list(result.scalars().all())
    already = await session.execute(
        select(Prediction.event_id).where(Prediction.user_id == llm_user.id)
    )
    predicted_ids = {row[0] for row in already.all()}
    to_predict = [e for e in upcoming if e.id not in predicted_ids]
    if not to_predict:
        return []

    context = await build_context(session, to_predict)
    answer = await client.complete_json(SYSTEM_PROMPT, context, session)
    saved = []
    for item in answer.get("predicciones", []):
        event = next((e for e in to_predict if e.id == item.get("event_id")), None)
        if event is None:
            continue
        prediction = Prediction(
            user_id=llm_user.id,
            event_id=event.id,
            home_score=item.get("home_score"),
            away_score=item.get("away_score"),
            positions=item.get("positions"),
        )
        session.add(prediction)
        saved.append(prediction)
    await session.commit()
    return saved
