"""Orígenes de líneas del panel: puerto USB serial real o entrada estándar (simulador)."""
import logging
import sys
import threading
from collections.abc import Callable, Iterator
from typing import IO, Protocol

logger = logging.getLogger("reactor_bridge.sources")

# Identificadores USB (VID) habituales de Arduino y de sus chips USB-serial clones.
_ARDUINO_VIDS = {0x2341, 0x2A03, 0x1A86, 0x0403, 0x10C4}
_SERIAL_NAME_HINTS = ("ttyACM", "ttyUSB", "usbmodem", "usbserial")


class LineSource(Protocol):
    def lines(self) -> Iterator[str]: ...

    def request_hello(self) -> None: ...

    def close(self) -> None: ...


class StdinSource:
    """Lee las líneas de un flujo de texto (por defecto stdin). Pensado para el simulador."""

    def __init__(self, stream: IO[str] | None = None) -> None:
        self._stream = stream if stream is not None else sys.stdin

    def lines(self) -> Iterator[str]:
        for raw in self._stream:
            line = raw.strip()
            if line:
                yield line

    def request_hello(self) -> None:
        """El simulador ya anuncia su HELLO al iniciar; no hay canal de vuelta."""

    def close(self) -> None:
        """Nada que liberar."""


def find_arduino_port() -> str:
    """Busca un puerto USB serial que parezca un Arduino. Lanza RuntimeError si no hay ninguno."""
    from serial.tools import list_ports

    candidates = []
    for info in list_ports.comports():
        looks_like_arduino = info.vid in _ARDUINO_VIDS or any(h in info.device for h in _SERIAL_NAME_HINTS)
        if looks_like_arduino:
            candidates.append(info.device)
    if not candidates:
        raise RuntimeError("no se encontró ningún Arduino por USB")
    return sorted(candidates)[0]


class SerialSource:
    """Lee el Arduino por USB serial y se reconecta si se desconecta el cable."""

    def __init__(
        self,
        port: str = "auto",
        baud: int = 9600,
        reconnect_seconds: float = 2.0,
        serial_factory: Callable[..., object] | None = None,
        port_finder: Callable[[], str] = find_arduino_port,
    ) -> None:
        self._port = port
        self._baud = baud
        self._reconnect_seconds = reconnect_seconds
        self._serial_factory = serial_factory
        self._port_finder = port_finder
        self._stop = threading.Event()
        self._connection = None

    def _open(self):
        factory = self._serial_factory
        if factory is None:
            import serial

            factory = serial.Serial
        port = self._port_finder() if self._port == "auto" else self._port
        logger.info("Abriendo %s a %d baudios", port, self._baud)
        return factory(port, self._baud, timeout=1)

    def lines(self) -> Iterator[str]:
        while not self._stop.is_set():
            try:
                self._connection = self._open()
                self.request_hello()
                while not self._stop.is_set():
                    raw = self._connection.readline()
                    if not raw:
                        continue  # timeout sin datos: revisar si hay que detenerse
                    line = raw.decode("ascii", errors="replace").strip()
                    if line:
                        yield line
            except (OSError, RuntimeError) as exc:
                logger.warning("Puerto serial no disponible (%s). Reintentando en %.1f s", exc, self._reconnect_seconds)
            finally:
                self._close_connection()
            self._stop.wait(self._reconnect_seconds)

    def request_hello(self) -> None:
        """Pide al Arduino repetir su HELLO (por si ya estaba encendido y no se reinició)."""
        if self._connection is None:
            return
        try:
            self._connection.write(b"WHO\n")
        except Exception as exc:  # noqa: BLE001 - no es crítico; el HELLO llega al reiniciar
            logger.warning("No se pudo enviar WHO: %s", exc)

    def _close_connection(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:  # noqa: BLE001
                pass
            self._connection = None

    def close(self) -> None:
        self._stop.set()
        self._close_connection()
