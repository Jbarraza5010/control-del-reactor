"""Patrón Observer: bus de eventos tipado dentro del proceso.

Quien publica (el servicio de cuentas) no conoce a quien escucha (el envío de correos),
así se agregan reacciones nuevas sin modificar el servicio. En el Sprint 3 el mismo
mecanismo propagará puntajes y ranking (ERS 7.3).
"""
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from app.shared.logger import get_logger

logger = get_logger()


@dataclass(frozen=True)
class UserRegistered:
    user_id: str
    email: str
    verification_token: str


@dataclass(frozen=True)
class PasswordResetRequested:
    user_id: str
    email: str
    reset_token: str


E = TypeVar("E")
Listener = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[type, list[Listener]] = defaultdict(list)

    def subscribe(self, event_type: type[E], listener: Callable[[E], None]) -> Callable[[], None]:
        """Registra un listener. Devuelve una función que cancela la suscripción."""
        self._listeners[event_type].append(listener)

        def unsubscribe() -> None:
            if listener in self._listeners[event_type]:
                self._listeners[event_type].remove(listener)

        return unsubscribe

    def publish(self, event: object) -> None:
        """Un listener que falla NO rompe a los demás ni a quien publicó: se registra el error."""
        for listener in list(self._listeners[type(event)]):
            try:
                listener(event)
            except Exception as exc:  # noqa: BLE001 - aislamiento deliberado de listeners
                logger.error(
                    "Falló un listener de evento",
                    extra={"extra_data": {"event": type(event).__name__, "error": str(exc)}},
                )
