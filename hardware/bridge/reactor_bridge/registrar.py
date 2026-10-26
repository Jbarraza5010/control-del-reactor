"""Anuncio del panel al backend (POST /api/v1/hardware/devices/announce, ver hardware/PROTOCOL.md)."""
import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

logger = logging.getLogger("reactor_bridge.registrar")


@dataclass(frozen=True)
class AnnounceResult:
    linked: bool
    pairing_code: str | None
    expires_at: datetime | None


class PanelRegistrar(Protocol):
    def announce(self, device_id: str, version: int) -> AnnounceResult | None:
        """Anuncia el panel. Devuelve None si el backend no respondió."""
        ...


def parse_expires_at(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class HttpRegistrar:
    def __init__(self, url: str, timeout_seconds: float = 2.0) -> None:
        self._url = url
        self._timeout = timeout_seconds

    def announce(self, device_id: str, version: int) -> AnnounceResult | None:
        body = json.dumps({"deviceId": device_id, "version": version}).encode("utf-8")
        request = urllib.request.Request(
            self._url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            logger.warning("El backend rechazó el anuncio del panel (%s): %s", exc.code, _error_message(exc))
            return None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            logger.warning("No se pudo anunciar el panel al backend (%s): %s", self._url, exc)
            return None
        return AnnounceResult(
            linked=bool(data.get("linked")),
            pairing_code=data.get("pairingCode"),
            expires_at=parse_expires_at(data.get("expiresAt")),
        )


def _error_message(exc: urllib.error.HTTPError) -> str:
    try:
        return json.loads(exc.read().decode("utf-8"))["error"]["message"]
    except Exception:  # noqa: BLE001 - el cuerpo es solo informativo
        return str(exc.reason)
