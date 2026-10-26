import threading
from dataclasses import replace

from app.domain.entities.hardware_panel import HardwarePanel
from app.domain.repositories.hardware_panel_repository import HardwarePanelRepository


class InMemoryHardwarePanelRepository(HardwarePanelRepository):
    """Paneles en memoria del proceso.

    Es la implementación que usa el backend en el Sprint 2: si el backend se reinicia, los paneles
    se olvidan y el puente los vuelve a anunciar al recibir un 404 (ver hardware/PROTOCOL.md).
    Devuelve copias para que nadie modifique el estado guardado sin pasar por save().
    """

    def __init__(self) -> None:
        self._panels: dict[str, HardwarePanel] = {}
        self._lock = threading.Lock()

    def find_by_id(self, entity_id: str) -> HardwarePanel | None:
        with self._lock:
            panel = self._panels.get(entity_id)
            return replace(panel) if panel else None

    def find_by_player(self, player_id: str) -> HardwarePanel | None:
        with self._lock:
            panel = next((p for p in self._panels.values() if p.player_id == player_id), None)
            return replace(panel) if panel else None

    def find_by_pairing_code(self, code: str) -> HardwarePanel | None:
        with self._lock:
            panel = next((p for p in self._panels.values() if p.pairing_code == code), None)
            return replace(panel) if panel else None

    def save(self, entity: HardwarePanel) -> HardwarePanel:
        with self._lock:
            self._panels[entity.device_id] = replace(entity)
            return replace(entity)

    def delete(self, device_id: str) -> None:
        with self._lock:
            self._panels.pop(device_id, None)
