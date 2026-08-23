from fastapi import APIRouter, Depends, Request
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.router import get_current_user
from app.chat.schemas import ChatRequest
from app.chat.service import responder
from app.core.rate_limit import limiter
from app.db.models import User
from app.deps import get_session
from app.llm.router import get_llm_client

router = APIRouter(prefix="/chat", tags=["chat"])


def chat_user_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth:
        return f"chat:{auth[-40:]}"
    return f"chat-ip:{get_remote_address(request)}"


@router.post("")
@limiter.limit("10/hour", key_func=chat_user_key)
async def chat(
    request: Request,
    payload: ChatRequest,
    session: AsyncSession = Depends(get_session),
    client=Depends(get_llm_client),
    current_user: User = Depends(get_current_user),
) -> dict:
    respuesta = await responder(session, client, payload.mensaje, payload.historial)
    return {"respuesta": respuesta}
