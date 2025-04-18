from collections.abc import Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import get_db  # the Depends(get_db) used in routes
from app.main import app  # your FastAPI app

# --- Create test DB engine and session ---
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


# --- Fixture for DB session ---
@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# --- Override FastAPI dependency ---
@pytest.fixture(scope="function", autouse=True)
def override_get_db(db: Session):
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


# --- Fixture for HTTP client ---
@pytest.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
