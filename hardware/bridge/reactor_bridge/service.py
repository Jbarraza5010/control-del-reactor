"""Lógica del puente: línea del panel -> mensaje JSON -> destino."""
import logging
import time
from collections.abc import Callable

from reactor_bridge.protocol import ButtonEvent, Hello, ProtocolError, build_message, parse_line
from reactor_bridge.sinks import EventSink
from reactor_bridge.sources import LineSource

logger = logging.getLogger("reactor_bridge.service")


def now_ms() -> int:
    return int(time.time() * 1000)


class BridgeService:
    def __init__(
        self,
        source: LineSource,
        sink: EventSink,
        clock_ms: Callable[[], int] = now_ms,
        device_id: str | None = None,
    ) -> None:
        self._source = source
        self._sink = sink
        self._clock_ms = clock_ms
        self._device_id = device_id
        self._fixed_device_id = device_id is not None

    @property
    def device_id(self) -> str | None:
        return self._device_id

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
        logger.info("Panel anunciado: %s (protocolo v%d)", hello.device_id, hello.version)

    def _on_button(self, event: ButtonEvent, received_at: int) -> None:
        if self._device_id is None:
            logger.warning("Botón %s %s descartado: el panel aún no se ha anunciado (HELLO)", event.button, event.event)
            return
        self._sink.send(build_message(self._device_id, event, received_at))
