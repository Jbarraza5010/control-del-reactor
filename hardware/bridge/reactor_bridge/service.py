"""Lógica del puente: línea del panel -> mensaje JSON -> destino.

Además se encarga de la vinculación (US-013, hardware/PROTOCOL.md):
- Al recibir el HELLO anuncia el panel al backend y muestra en consola el código de vinculación.
- Si el backend responde 404 a un botón (se reinició y olvidó el panel), lo vuelve a anunciar.
- Si responde 409 (panel sin vincular), recuerda el código; si ya venció, pide uno nuevo.
"""
import logging
import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime, timezone

from reactor_bridge.protocol import SUPPORTED_VERSION, ButtonEvent, Hello, ProtocolError, build_message, parse_line
from reactor_bridge.registrar import AnnounceResult, PanelRegistrar
from reactor_bridge.sinks import EventSink
from reactor_bridge.sources import LineSource

logger = logging.getLogger("reactor_bridge.service")

REANNOUNCE_MIN_SECONDS = 2.0  # evita anunciar en ráfaga si llegan muchos 404 seguidos
REMINDER_MIN_SECONDS = 5.0  # cada cuánto se repite el aviso "panel sin vincular"


def now_ms() -> int:
    return int(time.time() * 1000)


def print_to_console(text: str) -> None:
    # Va a stderr para no mezclarse con el JSON que imprime el sink stdout.
    print(text, file=sys.stderr, flush=True)


class BridgeService:
    def __init__(
        self,
        source: LineSource,
        sink: EventSink,
        clock_ms: Callable[[], int] = now_ms,
        device_id: str | None = None,
        registrar: PanelRegistrar | None = None,
        display: Callable[[str], None] = print_to_console,
        monotonic: Callable[[], float] = time.monotonic,
        utcnow: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._source = source
        self._sink = sink
        self._clock_ms = clock_ms
        self._device_id = device_id
        self._fixed_device_id = device_id is not None
        self._version = SUPPORTED_VERSION
        self._registrar = registrar
        self._display = display
        self._monotonic = monotonic
        self._utcnow = utcnow
        # El anuncio puede venir del hilo principal (HELLO) o del hilo del HttpSink (404/409).
        self._lock = threading.Lock()
        self._last_announce: float | None = None
        self._last_reminder: float | None = None
        self._pairing: AnnounceResult | None = None

    @property
    def device_id(self) -> str | None:
        return self._device_id

    @property
    def pairing(self) -> AnnounceResult | None:
        return self._pairing

    def run(self) -> None:
        """Procesa líneas hasta que el origen termine (o se interrumpa con Ctrl+C)."""
        for line in self._source.lines():
            self.handle_line(line)

    def handle_line(self, line: str) -> None:
        # El timestamp se toma apenas llega la línea, antes de cualquier otro trabajo.
        received_at = self._clock_ms()
        try:
            parsed = parse_line(line)
        except ProtocolError as exc:
            logger.warning("Línea descartada (%s): %r", exc, line)
            return

        if isinstance(parsed, Hello):
            self._on_hello(parsed)
        elif isinstance(parsed, ButtonEvent):
            self._on_button(parsed, received_at)

    def _on_hello(self, hello: Hello) -> None:
        if not self._fixed_device_id:
            self._device_id = hello.device_id
        self._version = hello.version
        logger.info("Panel anunciado: %s (protocolo v%d)", hello.device_id, hello.version)
        self.announce(force=True)

    def _on_button(self, event: ButtonEvent, received_at: int) -> None:
        if self._device_id is None:
            logger.warning("Botón %s %s descartado: el panel aún no se ha anunciado (HELLO)", event.button, event.event)
            return
        self._sink.send(build_message(self._device_id, event, received_at))

    # ---- Vinculación con el backend ------------------------------------------
    def announce(self, force: bool = False) -> None:
        """Anuncia el panel al backend y muestra el resultado. Sin registrar (modo stdout) no hace nada."""
        if self._registrar is None or self._device_id is None:
            return
        with self._lock:
            now = self._monotonic()
            if not force and self._last_announce is not None and now - self._last_announce < REANNOUNCE_MIN_SECONDS:
                return
            self._last_announce = now
            result = self._registrar.announce(self._device_id, self._version)
            if result is None:
                self._display("No se pudo anunciar el panel: ¿está corriendo el backend? Se reintentará al presionar un botón.")
                return
            self._pairing = result
            self._last_reminder = now
            self._show_pairing(result)

    def on_rejected(self, status: int, message: dict) -> None:
        """Lo llama el HttpSink cuando el backend responde a un botón con error HTTP."""
        if status == 404:
            logger.info("El backend no conoce el panel (404): se vuelve a anunciar")
            self.announce()
        elif status == 409:
            self._remind_or_renew()
        elif status == 400:
            logger.warning("El backend rechazó el evento por inválido (400): %s", message)
        else:
            logger.warning("El backend respondió %s al evento %s", status, message)

    def _remind_or_renew(self) -> None:
        pairing = self._pairing
        expired = pairing is None or pairing.pairing_code is None or (
            pairing.expires_at is not None and self._utcnow() >= pairing.expires_at
        )
        if expired:
            self.announce()  # el backend genera un código nuevo
            return
        now = self._monotonic()
        if self._last_reminder is not None and now - self._last_reminder < REMINDER_MIN_SECONDS:
            return
        self._last_reminder = now
        self._display(f"Panel sin vincular: ingresa el código {pairing.pairing_code} en el juego.")

    def _show_pairing(self, result: AnnounceResult) -> None:
        if result.linked:
            self._display(f"Panel {self._device_id} ya vinculado a un jugador: listo para jugar.")
            return
        expires = ""
        if result.expires_at is not None:
            expires = f" (vence a las {result.expires_at.astimezone().strftime('%H:%M')})"
        line = "=" * 52
        self._display(
            f"\n{line}\n"
            f"  CÓDIGO DE VINCULACIÓN DEL PANEL {self._device_id}:  {result.pairing_code}\n"
            f"  Ingrésalo en el juego{expires}.\n"
            f"{line}\n"
        )
