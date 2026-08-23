from fastapi import FastAPI

from app.core.config import get_settings
from app.events.router import router as events_router

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(events_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
