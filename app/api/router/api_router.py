from fastapi import APIRouter

from app.api.auth import api_auth
from app.api.user import api_user
from app.api.healthcheck import api_healthcheck


router = APIRouter()

router.include_router(
    api_healthcheck.router, tags=["health-check"], prefix="/healthcheck"
)
router.include_router(api_auth.router, tags=["login"], prefix="/auth")
router.include_router(api_user.router, tags=["user"], prefix="/users")
