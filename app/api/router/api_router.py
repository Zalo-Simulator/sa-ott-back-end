from fastapi import APIRouter

from app.api.auth import api_login
from app.api.user import api_user
from app.api.healthcheck import api_healthcheck
from app.api.auth import api_register

router = APIRouter()

router.include_router(api_healthcheck.router, tags=["health-check"], prefix="/healthcheck")
router.include_router(api_login.router, tags=["login"], prefix="/login")
router.include_router(api_register.router, tags=["register"], prefix="/register")
router.include_router(api_user.router, tags=["user"], prefix="/users")
