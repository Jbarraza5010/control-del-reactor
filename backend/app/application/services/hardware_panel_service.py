"""Casos de uso del panel físico (US-013): anunciar, vincular, desvincular y recibir botones.

Las reglas salen de hardware/PROTOCOL.md:
- El código de vinculación tiene 6 dígitos, vale 5 minutos y se usa una sola vez.
- Si un panel sin vincular se anuncia de nuevo, el código anterior se invalida y se genera otro.
- Un panel ya vinculado que se vuelve a anunciar conserva su vínculo (no se genera código).
- Un jugador tiene un solo panel y un panel pertenece a un solo jugador.

Cada cambio se publica en el EventBus (Observer); quien publica no sabe quién escucha
(el WebSocket de los clientes y, en el Sprint 3, el motor de juego).
"""
import re
import secrets
import threading
from collections.abc import Callable
from datetime import datetime, timezone

from app.domain.entities.hardware_panel import (
    BUTTON_EVENTS,
    BUTTONS,
    DEVICE_ID_PATTERN,
    PAIRING_CODE_PATTERN,
    PAIRING_CODE_TTL,
    PROTOCOL_VERSION,
    HardwarePanel,
)
from app.domain.repositories.hardware_panel_repository import HardwarePanelRepository
from app.shared.errors import ConflictError, NotFoundError, ValidationAppError
from app.shared.events import (
    EventBus,
    HardwareButtonEvent,
    PanelAnnounced,
    PanelLinked,
    PanelUnlinked,
)

_DEVICE_ID = re.compile(DEVICE_ID_PATTERN)
_PAIRING_CODE = re.compile(PAIRING_CODE_PATTERN)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _random_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class HardwarePanelService:
    def __init__(
        self,
        repository: HardwarePanelRepository,
        event_bus: EventBus,
        clock: Callable[[], datetime] = _utcnow,
        code_generator: Callable[[], str] = _random_code,
    ) -> None:
        self._repository = repository
        self._bus = event_bus
        self._clock = clock
        self._code_generator = code_generator
        # Las rutas síncronas de FastAPI corren en varios hilos: el candado evita, por ejemplo,
        # que dos jugadores usen el mismo código al mismo tiempo.
        self._lock = threading.Lock()

    # ---- Lo llama el puente ------------------------------------------------
    def announce(self, device_id: str, version: int) -> HardwarePanel:
        self._check_device_id(device_id)
        if version != PROTOCOL_VERSION:
            raise ValidationAppError(
                "Versión de protocolo no soportada", {"version": version, "supported": [PROTOCOL_VERSION]}
            )
        with self._lock:
            panel = self._repository.find_by_id(device_id) or HardwarePanel(device_id=device_id)
            if not panel.is_linked:
                panel.pairing_code = self._new_unique_code()
                panel.pairing_expires_at = self._clock() + PAIRING_CODE_TTL
            panel = self._repository.save(panel)
        self._bus.publish(PanelAnnounced(device_id=panel.device_id, pairing_code=panel.pairing_code))
        return panel

    def handle_button(self, device_id: str, button: str, event: str, timestamp: int) -> None:
        if button not in BUTTONS:
            raise ValidationAppError("Botón desconocido", {"button": button, "allowed": list(BUTTONS)})
        if event not in BUTTON_EVENTS:
            raise ValidationAppError("Evento desconocido", {"event": event, "allowed": list(BUTTON_EVENTS)})
        panel = self._repository.find_by_id(device_id)
        if panel is None:
            raise NotFoundError("Panel no anunciado; el puente debe anunciarlo de nuevo")
        if not panel.is_linked:
            raise ConflictError("El panel no está vinculado a ningún jugador")
        self._bus.publish(
            HardwareButtonEvent(
                device_id=device_id, player_id=panel.player_id, button=button, event=event, timestamp=timestamp
            )
        )

    # ---- Lo llama el cliente (jugador con sesión) --------------------------
    def link(self, player_id: str, pairing_code: str) -> HardwarePanel:
        if not _PAIRING_CODE.match(pairing_code):
            raise ValidationAppError("El código de vinculación debe tener 6 dígitos")
        with self._lock:
            now = self._clock()
            panel = self._repository.find_by_pairing_code(pairing_code)
            if panel is None or not panel.accepts_pairing_code(pairing_code, now):
                raise NotFoundError("Código de vinculación inválido o expirado")
            if self._repository.find_by_player(player_id) is not None:
                raise ConflictError("El jugador ya tiene otro panel vinculado")
            panel.player_id = player_id
            panel.linked_at = now
            panel.pairing_code = None  # un solo uso
            panel.pairing_expires_at = None
            panel = self._repository.save(panel)
        self._bus.publish(PanelLinked(device_id=panel.device_id, player_id=player_id))
        return panel

    def get_link(self, player_id: str) -> HardwarePanel:
        panel = self._repository.find_by_player(player_id)
        if panel is None:
            raise NotFoundError("No tienes un panel vinculado")
        return panel

    def unlink(self, player_id: str) -> None:
        with self._lock:
            panel = self._repository.find_by_player(player_id)
            if panel is None:
                raise NotFoundError("No tienes un panel vinculado")
            # Se olvida el panel: para volver a vincularlo debe anunciarse y obtener un código nuevo.
            self._repository.delete(panel.device_id)
        self._bus.publish(PanelUnlinked(device_id=panel.device_id, player_id=player_id))

    # ---- Auxiliares --------------------------------------------------------
    @staticmethod
    def _check_device_id(device_id: str) -> None:
        if not _DEVICE_ID.match(device_id):
            raise ValidationAppError("deviceId con formato inválido", {"deviceId": device_id})

    def _new_unique_code(self) -> str:
        for _ in range(50):
            code = self._code_generator()
            if self._repository.find_by_pairing_code(code) is None:
                return code
        raise RuntimeError("No se pudo generar un código de vinculación único")
