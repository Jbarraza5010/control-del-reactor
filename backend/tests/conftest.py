from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.application.ports.database_health import DatabaseHealth
from app.application.services.register_mail_listeners import register_mail_listeners
from app.container import Container
from app.domain.entities.user import User
from app.infrastructure.mail.console_mailer import ConsoleMailer
from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
from app.infrastructure.persistence.sql.models import Base
from app.infrastructure.persistence.sql.session import create_session_factory
from app.infrastructure.persistence.sql.sql_auth_token_repository import SqlAuthTokenRepository
from app.infrastructure.persistence.sql.sql_user_repository import SqlUserRepository
from app.shared.events import EventBus


class FakeDatabaseHealth(DatabaseHealth):
    def __init__(self, up: bool = True) -> None:
        self.up = up

    def ping(self) -> None:
        if not self.up:
            raise RuntimeError("sin conexión")


def make_container(db_up: bool = True) -> Container:
    bus = EventBus()
    mailer = ConsoleMailer()
    register_mail_listeners(bus, mailer)
    return Container(
        event_bus=bus,
        mailer=mailer,
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
def sql_session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return create_session_factory(engine)


@pytest.fixture
def sql_repository(sql_session_factory):
    """Repositorio SQL real sobre SQLite en memoria (misma lógica que con PostgreSQL)."""
    return SqlUserRepository(sql_session_factory)


@pytest.fixture
def sql_token_repository(sql_session_factory):
    return SqlAuthTokenRepository(sql_session_factory)
