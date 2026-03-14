"""
Database configuration and session management for Ganga Guardian.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./ganga.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on startup."""
    import models  # noqa: F401 - registers models with Base
    Base.metadata.create_all(bind=engine)
    # Migrate: add new columns if old schema exists (idempotent)
    from sqlalchemy import text
    migs = [
        "ALTER TABLE sensor_data ADD COLUMN risk_level VARCHAR(50)",
        "ALTER TABLE sensor_data ADD COLUMN created_at DATETIME",
        "ALTER TABLE complaints ADD COLUMN status VARCHAR(50)",
        "ALTER TABLE complaints ADD COLUMN created_at DATETIME",
    ]
    for sql in migs:
        try:
            with engine.begin() as conn:
                conn.execute(text(sql))
        except Exception:
            pass  # column may already exist
    logger.info("Database initialized")
