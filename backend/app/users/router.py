from fastapi import APIRouter, Depends

from app.auth.router import get_current_user
from app.db.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=dict)
async def me(current_user: User = Depends(get_current_user)) -> dict:
    return {"id": current_user.id, "email": current_user.email, "username": current_user.username}
