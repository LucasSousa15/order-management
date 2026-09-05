from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.database.config import database_settings


class Base(DeclarativeBase):
    pass


class Database:

    def __init__(self, database_url: str) -> None:
        self.engine: Engine = create_engine(database_url, pool_pre_ping=True)
        self._session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def session(self) -> Session:
        return self._session_factory()


database = Database(database_settings.url)


def get_session() -> Iterator[Session]:
    with database.session() as session:
        yield session
