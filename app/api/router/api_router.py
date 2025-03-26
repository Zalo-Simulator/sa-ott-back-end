from fastapi import APIRouter

from app.api.auth.api_auth import auth_router, router as protected_auth_router
from app.api.user import api_user
from app.api.test import api_test
from app.api.friend import api_friend
from app.api.healthcheck import api_healthcheck


router = APIRouter()


router.include_router(auth_router, tags=["register"], prefix="/auth")         
router.include_router(protected_auth_router, tags=["login"], prefix="/auth")  
router.include_router(
    api_healthcheck.router, tags=["health-check"], prefix="/healthcheck"
)
# router.include_router(api_auth.router, tags=["login"], prefix="/auth")
router.include_router(api_user.router, tags=["user"], prefix="/users")
router.include_router(api_test.router, tags=["test"], prefix="/tests")
router.include_router(api_friend.router, tags=["friend"], prefix="/friends")
