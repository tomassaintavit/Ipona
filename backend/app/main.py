from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.events.router import router as events_router
from app.predictions.router import router as predictions_router
from app.scoring.router import router as scoring_router
from app.users.router import router as users_router

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.include_router(events_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(predictions_router)
app.include_router(scoring_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
