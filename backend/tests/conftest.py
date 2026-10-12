from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.application.ports.database_health import DatabaseHealth
from app.container import Container
from app.domain.entities.user import User
from app.infrastructure.mail.console_mailer import ConsoleMailer
from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
from app.infrastructure.persistence.sql.models import Base
from app.infrastructure.persistence.sql.session import create_session_factory
from app.infrastructure.persistence.sql.sql_user_repository import SqlUserRepository
from app.shared.events import EventBus


class FakeDatabaseHealth(DatabaseHealth):
    def __init__(self, up: bool = True) -> None:
        self.up = up

    def ping(self) -> None:
        if not self.up:
            raise RuntimeError("sin conexión")


def make_container(db_up: bool = True) -> Container:
    return Container(
        event_bus=EventBus(),
        mailer=ConsoleMailer(),
        user_repository=InMemoryUserRepository(),
        database_health=FakeDatabaseHealth(db_up),
    )


def make_user(**overrides) -> User:
    data = dict(
        id="1",
        username="Ulfran",
        email="Ulfran@tec.ac.cr",
        password_hash="hash",
        status="PENDIENTE_VERIFICACION",
        created_at=datetime(2026, 10, 12, tzinfo=timezone.utc),
    )
    data.update(overrides)
    return User(**data)


@pytest.fixture
def sql_repository():
    """Repositorio SQL real sobre SQLite en memoria (misma lógica que con PostgreSQL)."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return SqlUserRepository(create_session_factory(engine))
