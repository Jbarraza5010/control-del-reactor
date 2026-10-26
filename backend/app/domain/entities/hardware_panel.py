"""Entidad de dominio "Panel físico" (US-013). Python puro: no depende de FastAPI ni de SQLAlchemy.

Reglas del contrato en hardware/PROTOCOL.md ("Vinculación del panel").
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

BUTTONS = ("UP", "DOWN", "LEFT", "RIGHT", "ACTION")
BUTTON_EVENTS = ("press", "release")
PROTOCOL_VERSION = 1
DEVICE_ID_PATTERN = r"^[A-Za-z0-9_-]{1,32}$"
PAIRING_CODE_PATTERN = r"^\d{6}$"
PAIRING_CODE_TTL = timedelta(minutes=5)


@dataclass
class HardwarePanel:
    device_id: str
    player_id: str | None = None
    linked_at: datetime | None = None
    pairing_code: str | None = None
    pairing_expires_at: datetime | None = None

    @property
    def is_linked(self) -> bool:
        return self.player_id is not None

    def accepts_pairing_code(self, code: str, now: datetime) -> bool:
        """El código sirve si coincide, no ha vencido y el panel sigue sin dueño."""
        return (
            not self.is_linked
            and self.pairing_code == code
            and self.pairing_expires_at is not None
            and now < self.pairing_expires_at
        )
