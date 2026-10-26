"""Composition root: el ÚNICO lugar donde se eligen las implementaciones concretas
y se conectan entre sí (inyección de dependencias manual, sin librerías)."""
from dataclasses import dataclass, field

from sqlalchemy import Engine

from app.application.ports.database_health import DatabaseHealth
from app.application.ports.mailer import Mailer
from app.application.ports.player_identity import PlayerIdentity
from app.application.services.hardware_panel_service import HardwarePanelService
from app.application.services.register_hardware_listeners import register_hardware_listeners
from app.application.services.register_mail_listeners import register_mail_listeners
from app.config import Settings
from app.domain.repositories.hardware_panel_repository import HardwarePanelRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.auth.dev_player_identity import DevPlayerIdentity
from app.infrastructure.mail.mailer_factory import MailerFactory
from app.infrastructure.persistence.memory.in_memory_hardware_panel_repository import (
    InMemoryHardwarePanelRepository,
)
from app.infrastructure.persistence.sql.session import create_db_engine, create_session_factory
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
    # Panel físico (US-013). Tienen valor por defecto para que los contenedores de prueba existentes
    # sigan funcionando sin cambios.
    hardware_panels: HardwarePanelRepository = field(default_factory=InMemoryHardwarePanelRepository)
    # TEMPORAL: el login aún no emite tokens. Cuando exista, cambiar SOLO esta implementación.
    player_identity: PlayerIdentity = field(default_factory=DevPlayerIdentity)
    hardware_service: HardwarePanelService = field(init=False)

    def __post_init__(self) -> None:
        self.hardware_service = HardwarePanelService(self.hardware_panels, self.event_bus)


def build_container(settings: Settings) -> Container:
    engine = create_db_engine(settings.database_url)
    event_bus = EventBus()
    mailer = MailerFactory.create(settings)
    register_mail_listeners(event_bus, mailer)
    register_hardware_listeners(event_bus)
    logger.warning(
        "Identificación de jugador de DESARROLLO activa en las rutas de hardware: el token es el id del jugador"
    )
    return Container(
        event_bus=event_bus,
        mailer=mailer,
        user_repository=SqlUserRepository(create_session_factory(engine)),
        database_health=SqlDatabaseHealth(engine),
        engine=engine,
    )
