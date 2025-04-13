from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from collections.abc import Generator  # ✅ dùng đúng Generator cho yield

# Create SQLAlchemy engine
engine: Engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Typed sessionmaker that creates Session objects
SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Dependency function for getting a database session (e.g., in FastAPI)
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
