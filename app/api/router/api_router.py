from fastapi import APIRouter

from app.api.auth.api_auth import auth_router
from app.api.auth.api_auth import router as protected_auth_router
from app.api.chat import api_chat
from app.api.friend import api_friend
from app.api.healthcheck import api_healthcheck
from app.api.test import api_test
from app.api.user import api_user
from app.api.ws import api_web_socket

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
router.include_router(api_chat.router, tags=["chat"], prefix="/chats")
router.include_router(api_web_socket.router, tags=["ws"], prefix="/ws")
