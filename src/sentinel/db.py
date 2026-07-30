"""Database engine and session setup for Sentinel.

v1 target: local SQLite file. No Postgres/Docker here yet — that's v2+.
"""

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# SQLite file will live at the project root as sentinel.db
DATABASE_URL = "sqlite:///./sentinel.db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional database session as a context manager.

    Usage:
        with get_session() as session:
            session.add(some_object)
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()