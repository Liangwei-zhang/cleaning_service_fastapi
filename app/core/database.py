from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from sqlalchemy.pool import NullPool

from app.core.config import settings


# Create engine based on database type
if settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
else:
    # SQLite (fallback for development)
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )


def init_db():
    """Initialize database tables"""
    from app.models.cleaning import Cleaner, Host, Property, Order
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session
