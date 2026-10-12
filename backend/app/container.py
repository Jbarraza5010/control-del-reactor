"""Composition root: el ÚNICO lugar donde se eligen las implementaciones concretas
y se conectan entre sí (inyección de dependencias manual, sin librerías)."""
from dataclasses import dataclass

from sqlalchemy import Engine

from app.application.ports.database_health import DatabaseHealth
from app.application.ports.mailer import Mailer
from app.application.services.register_mail_listeners import register_mail_listeners
from app.config import Settings
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.mail.mailer_factory import MailerFactory
from app.infrastructure.persistence.sql.session import create_db_engine, create_session_factory
from app.infrastructure.persistence.sql.sql_database_health import SqlDatabaseHealth
from app.infrastructure.persistence.sql.sql_user_repository import SqlUserRepository
from app.shared.events import EventBus


@dataclass
class Container:
    event_bus: EventBus
    mailer: Mailer
    user_repository: UserRepository
    database_health: DatabaseHealth
    engine: Engine | None = None


def build_container(settings: Settings) -> Container:
    engine = create_db_engine(settings.database_url)
    event_bus = EventBus()
    mailer = MailerFactory.create(settings)
    register_mail_listeners(event_bus, mailer)
    return Container(
        event_bus=event_bus,
        mailer=mailer,
        user_repository=SqlUserRepository(create_session_factory(engine)),
        database_health=SqlDatabaseHealth(engine),
        engine=engine,
    )
