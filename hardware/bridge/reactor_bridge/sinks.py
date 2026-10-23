"""Destinos de los mensajes del panel: consola (pruebas) o backend por HTTP."""
import json
import logging
import queue
import sys
import threading
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import IO, Protocol

logger = logging.getLogger("reactor_bridge.sinks")

# Se llama cuando el backend responde con un error HTTP: (código, mensaje enviado).
RejectionHandler = Callable[[int, dict], None]


class EventSink(Protocol):
    def send(self, message: dict) -> None: ...

    def close(self) -> None: ...


class StdoutSink:
    """Imprime cada mensaje como una línea JSON. Sirve para probar sin backend."""

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream = stream if stream is not None else sys.stdout

    def send(self, message: dict) -> None:
        self._stream.write(json.dumps(message, separators=(",", ":")) + "\n")
        self._stream.flush()

    def close(self) -> None:
        """Nada que liberar."""


class HttpSink:
    """Envía cada mensaje al backend con POST JSON.

    El envío se hace en un hilo aparte para que un backend lento no bloquee la lectura de botones.
    Los mensajes se envían en orden; si el backend falla, el mensaje se descarta y se registra
    (no se reintenta: un movimiento que llega tarde es peor que uno perdido, RNF-02).
    Si el backend responde con un error HTTP (404, 409...), se avisa a `on_rejected` para que el
    puente reaccione (por ejemplo, volver a anunciar el panel).
    """

    _STOP = object()

    def __init__(
        self,
        url: str,
        timeout_seconds: float = 0.4,
        max_pending: int = 256,
        on_rejected: RejectionHandler | None = None,
    ) -> None:
        self._url = url
        self._timeout = timeout_seconds
        self._on_rejected = on_rejected
        self._queue: queue.Queue = queue.Queue(maxsize=max_pending)
        self._worker = threading.Thread(target=self._run, name="http-sink", daemon=True)
        self._worker.start()

    def set_rejection_handler(self, handler: RejectionHandler | None) -> None:
        self._on_rejected = handler

    def send(self, message: dict) -> None:
        try:
            self._queue.put_nowait(message)
        except queue.Full:
            logger.warning("Cola de envío llena; se descarta %s", message)

    def close(self) -> None:
        self._queue.put(self._STOP)
        self._worker.join(timeout=2)

    def _run(self) -> None:
        while True:
            message = self._queue.get()
            if message is self._STOP:
                return
            self._post(message)

    def _post(self, message: dict) -> None:
        body = json.dumps(message).encode("utf-8")
        request = urllib.request.Request(
            self._url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout):
                pass
        except urllib.error.HTTPError as exc:  # el backend respondió, pero con error
            self._handle_rejection(exc.code, message)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.warning("No se pudo enviar al backend (%s): %s", self._url, exc)

    def _handle_rejection(self, status: int, message: dict) -> None:
        if self._on_rejected is None:
            logger.warning("El backend rechazó el evento (%s): %s", status, message)
            return
        try:
            self._on_rejected(status, message)
        except Exception:  # noqa: BLE001 - un fallo aquí no debe detener el envío
            logger.exception("Falló el manejo del rechazo %s", status)
