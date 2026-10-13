"""Protocolo del panel: interpreta las líneas del Arduino y arma el mensaje JSON.

Formatos documentados en hardware/README.md (sección "Comunicación USB") y hardware/PROTOCOL.md (mensaje al backend).
"""
import re
from dataclasses import dataclass

BUTTONS = frozenset({"UP", "DOWN", "LEFT", "RIGHT", "ACTION"})
BUTTON_EVENTS = frozenset({"press", "release"})
SUPPORTED_VERSION = 1

_DEVICE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class ProtocolError(ValueError):
    """La línea recibida no cumple el protocolo del panel."""


@dataclass(frozen=True)
class Hello:
    device_id: str
    version: int


@dataclass(frozen=True)
class ButtonEvent:
    button: str
    event: str


def parse_line(raw: str) -> Hello | ButtonEvent:
    """Convierte una línea del Arduino en un objeto. Lanza ProtocolError si es inválida."""
    parts = raw.strip().split()
    if not parts:
        raise ProtocolError("línea vacía")

    kind = parts[0]
    if kind == "HELLO":
        return _parse_hello(parts)
    if kind == "BTN":
        return _parse_button(parts)
    raise ProtocolError(f"tipo de mensaje desconocido: {kind!r}")


def _parse_hello(parts: list[str]) -> Hello:
    if len(parts) != 3:
        raise ProtocolError("HELLO requiere: HELLO <deviceId> <version>")
    _, device_id, version_text = parts
    if not _DEVICE_ID_PATTERN.match(device_id):
        raise ProtocolError(f"deviceId inválido: {device_id!r}")
    if not version_text.isdigit():
        raise ProtocolError(f"versión inválida: {version_text!r}")
    version = int(version_text)
    if version != SUPPORTED_VERSION:
        raise ProtocolError(f"versión de protocolo no soportada: {version}")
    return Hello(device_id=device_id, version=version)


def _parse_button(parts: list[str]) -> ButtonEvent:
    if len(parts) != 3:
        raise ProtocolError("BTN requiere: BTN <BOTON> press|release")
    _, button, event = parts
    if button not in BUTTONS:
        raise ProtocolError(f"botón desconocido: {button!r}")
    if event not in BUTTON_EVENTS:
        raise ProtocolError(f"evento desconocido: {event!r}")
    return ButtonEvent(button=button, event=event)


def build_message(device_id: str, event: ButtonEvent, timestamp_ms: int) -> dict:
    """Mensaje de evento de botón que recibe el backend (ver PROTOCOL.md)."""
    return {
        "deviceId": device_id,
        "button": event.button,
        "event": event.event,
        "timestamp": timestamp_ms,
    }
