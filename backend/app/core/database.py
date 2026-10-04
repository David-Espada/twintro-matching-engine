from functools import lru_cache

from app.core.config import get_settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})


def get_session():
    with Session(get_engine()) as session:
        yield session


def initialize_database() -> None:
    from app.models import match_result, profile  # noqa: F401

    engine = get_engine()
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(connection)


if __name__ == "__main__":
    initialize_database()
    print("PostgreSQL tables and pgvector indexes initialized.")
