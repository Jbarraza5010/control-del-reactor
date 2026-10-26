"""Composition root: el ÚNICO lugar donde se eligen las implementaciones concretas
y se conectan entre sí (inyección de dependencias manual, sin librerías)."""
from dataclasses import dataclass, field

from sqlalchemy import Engine

from app.application.ports.database_health import DatabaseHealth
from app.application.ports.mailer import Mailer
from app.application.ports.player_identity import PlayerIdentity
from app.application.services.auth_service import AuthService
from app.application.services.hardware_panel_service import HardwarePanelService
from app.application.services.register_hardware_listeners import register_hardware_listeners
from app.application.services.register_mail_listeners import register_mail_listeners
from app.config import Settings
from app.domain.repositories.auth_token_repository import AuthTokenRepository
from app.domain.repositories.hardware_panel_repository import HardwarePanelRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.auth.dev_player_identity import DevPlayerIdentity
from app.infrastructure.mail.mailer_factory import MailerFactory
from app.infrastructure.persistence.memory.in_memory_auth_token_repository import (
    InMemoryAuthTokenRepository,
)
from app.infrastructure.persistence.memory.in_memory_hardware_panel_repository import (
    InMemoryHardwarePanelRepository,
)
from app.infrastructure.persistence.sql.session import create_db_engine, create_session_factory
from app.infrastructure.persistence.sql.sql_auth_token_repository import SqlAuthTokenRepository
from app.infrastructure.persistence.sql.sql_database_health import SqlDatabaseHealth
from app.infrastructure.persistence.sql.sql_user_repository import SqlUserRepository
from app.shared.events import EventBus
from app.shared.logger import get_logger

logger = get_logger()


@dataclass
class Container:
    event_bus: EventBus
    mailer: Mailer
    user_repository: UserRepository
    database_health: DatabaseHealth
    engine: Engine | None = None
    # Panel físico (US-013) y tokens de autenticación (US-004/005/007).
    # Tienen valor por defecto para que los contenedores de prueba existentes sigan funcionando sin cambios.
    hardware_panels: HardwarePanelRepository = field(default_factory=InMemoryHardwarePanelRepository)
    auth_tokens: AuthTokenRepository = field(default_factory=InMemoryAuthTokenRepository)
    player_identity: PlayerIdentity = field(default_factory=DevPlayerIdentity)
    hardware_service: HardwarePanelService = field(init=False)
    auth_service: AuthService = field(init=False)

    def __post_init__(self) -> None:
        self.hardware_service = HardwarePanelService(self.hardware_panels, self.event_bus)
        self.auth_service = AuthService(self.user_repository, self.auth_tokens, self.event_bus)
        if isinstance(self.player_identity, DevPlayerIdentity) and self.player_identity._auth_tokens is None:
            self.player_identity = DevPlayerIdentity(self.auth_tokens)


def build_container(settings: Settings) -> Container:
    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    event_bus = EventBus()
    mailer = MailerFactory.create(settings)
    register_mail_listeners(event_bus, mailer)
    register_hardware_listeners(event_bus)
    auth_tokens = SqlAuthTokenRepository(session_factory)
    return Container(
        event_bus=event_bus,
        mailer=mailer,
        user_repository=SqlUserRepository(session_factory),
        database_health=SqlDatabaseHealth(engine),
        engine=engine,
        auth_tokens=auth_tokens,
        player_identity=DevPlayerIdentity(auth_tokens),
    )
