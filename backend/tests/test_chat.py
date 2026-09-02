import asyncio
import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.chat.router import chat_user_key
from app.core.rate_limit import limiter
from app.db.models import Base, Prediction, SportEvent, User
from app.deps import get_session
from app.llm.router import get_llm_client
from app.main import app

from tests.conftest import make_test_engine


class FakeLLMConTools:
    def __init__(self, script):
        self.script = list(script)
        self._ultimo = {"role": "assistant", "content": ""}
        self.llamadas = 0

    async def complete_json(self, *a, **k):
        raise NotImplementedError

    async def chat_with_tools(self, messages, tools, session):
        self.llamadas += 1
        if not self.script:
            self.script = [self._ultimo]
        paso = self.script.pop(0)
        self._ultimo = paso
        from app.db.models import LLMCall

        session.add(
            LLMCall(provider="fake", model="m", prompt_tokens=10, completion_tokens=5, total_tokens=15)
        )
        await session.commit()
        return paso


async def _seed():
    from sqlalchemy import select

    engine = make_test_engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with factory() as session:
            user = User(email="c@ipona.ar", username="charly", password_hash="x")
            pasado = dt.datetime.now(dt.UTC) - dt.timedelta(days=3)
            evento = SportEvent(
                provider="espn",
                provider_event_id="p1",
                sport="futbol",
                league="Liga",
                start_time_utc=pasado,
                status="finalizado",
                home_team="Racing Club",
                away_team="Boca Juniors",
                final_home_score=2,
                final_away_score=1,
            )
            session.add_all([user, evento])
            await session.flush()
            session.add(
                Prediction(user_id=user.id, event_id=evento.id, home_score=2, away_score=1, points=3.0)
            )
            futuro = dt.datetime.now(dt.UTC) + dt.timedelta(hours=5)
            session.add(
                SportEvent(
                    provider="espn",
                    provider_event_id="f1x",
                    sport="futbol",
                    league="Liga",
                    start_time_utc=futuro,
                    status="programado",
                    home_team="River Plate",
                    away_team="Vélez",
                )
            )
            await session.commit()
            return (await session.execute(select(User).where(User.username == "charly"))).scalar_one().id
    finally:
        await engine.dispose()


@pytest.fixture(autouse=True)
def reset_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def client():
    user_id = asyncio.run(_seed())

    async def override_session():
        engine = make_test_engine()
        factory = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with factory() as session:
                yield session
        finally:
            await engine.dispose()

    from app.core.security import create_access_token

    headers = {"Authorization": f"Bearer {create_access_token(user_id)}"}
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as c:
        c.headers.update(headers)
        yield c
    app.dependency_overrides.clear()
    app.dependency_overrides.pop(get_llm_client, None)


def instalar_llm(script):
    fake = FakeLLMConTools(script)
    app.dependency_overrides[get_llm_client] = lambda: fake
    return fake


def test_chat_con_herramienta_responde(client):
    fake = instalar_llm(
        [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "t1",
                        "type": "function",
                        "function": {
                            "name": "ultimos_partidos",
                            "arguments": '{"equipo": "Racing Club"}',
                        },
                    }
                ],
            },
            {"role": "assistant", "content": "Racing ganó 2-1 a Boca."},
        ]
    )

    response = client.post("/chat", json={"mensaje": "como salio racing?"})

    assert response.status_code == 200
    assert response.json()["respuesta"] == "Racing ganó 2-1 a Boca."
    assert fake.llamadas == 2


def test_chat_sin_herramienta_responde_directo(client):
    instalar_llm([{"role": "assistant", "content": "Hola! Que queres saber?"}])

    response = client.post("/chat", json={"mensaje": "hola"})

    assert response.json()["respuesta"] == "Hola! Que queres saber?"


def test_herramienta_desconocida_no_falla(client):
    instalar_llm(
        [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "t9",
                        "type": "function",
                        "function": {"name": "borrar_base_de_datos", "arguments": "{}"},
                    }
                ],
            },
            {"role": "assistant", "content": "No puedo hacer eso."},
        ]
    )

    response = client.post("/chat", json={"mensaje": "borra todo"})

    assert response.status_code == 200
    assert response.json()["respuesta"] == "No puedo hacer eso."


def test_chat_requiere_login(client):
    token = client.headers["Authorization"]
    del client.headers["Authorization"]
    try:
        response = client.post("/chat", json={"mensaje": "hola"})
    finally:
        client.headers["Authorization"] = token
    assert response.status_code == 401


def test_chat_rate_limit_por_usuario(client):
    instalar_llm([{"role": "assistant", "content": "ok"}])

    ultima = None
    for i in range(11):
        ultima = client.post("/chat", json={"mensaje": f"pregunta {i}"})
    assert ultima.status_code == 429


def test_chat_con_historial_como_pydantic(client):
    instalar_llm([{"role": "assistant", "content": "respuesta con historial"}])

    response = client.post(
        "/chat",
        json={
            "mensaje": "otra pregunta",
            "historial": [{"role": "user", "content": "pregunta previa"}],
        },
    )

    assert response.status_code == 200
    assert response.json()["respuesta"] == "respuesta con historial"


def test_system_prompt_incluye_reglas():
    from app.chat.service import SYSTEM_PROMPT

    assert "reglas del juego" in SYSTEM_PROMPT.lower()
    assert "3 puntos" in SYSTEM_PROMPT
    assert "podio" in SYSTEM_PROMPT


def test_chat_user_key_distingue_tokens():
    request_a = type("R", (), {"headers": {"authorization": "Bearer aaaa"}, "client": None})()
    request_b = type("R", (), {"headers": {"authorization": "Bearer bbbb"}, "client": None})()

    assert chat_user_key(request_a) != chat_user_key(request_b)


def test_tools_ultimos_particos_busca_insensible():
    asyncio.run(_verificar_busqueda())


async def _verificar_busqueda():
    engine = make_test_engine()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            from app.chat.tools import ultimos_partidos

            partidos = await ultimos_partidos(session, "racing club")
            assert len(partidos) == 1
            assert partidos[0]["marcador"] == "2-1"
    finally:
        await engine.dispose()
