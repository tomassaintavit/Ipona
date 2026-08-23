from dataclasses import dataclass

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import LLMCall


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


PROVIDERS = {
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "key_setting": "cerebras_api_key",
        "model_setting": "cerebras_model",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_setting": "groq_api_key",
        "model_setting": "groq_model",
    },
}


class LLMClient:
    async def complete_json(self, system_prompt: str, user_prompt: str, session: AsyncSession) -> dict:
        settings = get_settings()
        primary = settings.llm_provider
        fallback = next(name for name in PROVIDERS if name != primary)
        try:
            return await self._call(primary, system_prompt, user_prompt, session)
        except Exception:
            return await self._call(fallback, system_prompt, user_prompt, session)

    async def chat_with_tools(self, messages: list[dict], tools: list[dict], session: AsyncSession) -> dict:
        settings = get_settings()
        primary = settings.llm_provider
        fallback = next(name for name in PROVIDERS if name != primary)
        try:
            return await self._call_tools(primary, messages, tools, session)
        except Exception:
            return await self._call_tools(fallback, messages, tools, session)

    async def _call_tools(self, provider: str, messages: list[dict], tools: list[dict], session: AsyncSession) -> dict:
        import json

        settings = get_settings()
        config = PROVIDERS[provider]
        api_key = getattr(settings, config["key_setting"])
        model = getattr(settings, config["model_setting"])
        client = AsyncOpenAI(base_url=config["base_url"], api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )
        usage = response.usage
        session.add(
            LLMCall(
                provider=provider,
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
        )
        await session.commit()
        message = response.choices[0].message
        result = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ]
        return result

    async def _call(self, provider: str, system_prompt: str, user_prompt: str, session: AsyncSession) -> dict:
        settings = get_settings()
        config = PROVIDERS[provider]
        api_key = getattr(settings, config["key_setting"])
        model = getattr(settings, config["model_setting"])
        client = AsyncOpenAI(base_url=config["base_url"], api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        usage = response.usage
        session.add(
            LLMCall(
                provider=provider,
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            )
        )
        await session.commit()
        import json

        return json.loads(response.choices[0].message.content)
