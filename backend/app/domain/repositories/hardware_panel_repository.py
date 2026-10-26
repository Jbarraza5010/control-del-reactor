"""Puerto de persistencia de los paneles físicos (patrón Repository)."""
from abc import abstractmethod

from app.domain.entities.hardware_panel import HardwarePanel
from app.domain.repositories.repository import Repository


class HardwarePanelRepository(Repository[HardwarePanel, str]):
    @abstractmethod
    def find_by_player(self, player_id: str) -> HardwarePanel | None: ...

    @abstractmethod
    def find_by_pairing_code(self, code: str) -> HardwarePanel | None: ...

    @abstractmethod
    def delete(self, device_id: str) -> None: ...
