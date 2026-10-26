"""Observador de los eventos del panel: deja constancia en el log (PROTOCOL.md, "Eventos internos").

Los botones no se registran uno por uno para no llenar el log.
"""
from app.shared.events import EventBus, PanelAnnounced, PanelLinked, PanelUnlinked
from app.shared.logger import get_logger

logger = get_logger()


def register_hardware_listeners(bus: EventBus) -> None:
    def on_announced(event: PanelAnnounced) -> None:
        logger.info(
            "Panel anunciado",
            extra={"extra_data": {"deviceId": event.device_id, "linked": event.pairing_code is None}},
        )

    def on_linked(event: PanelLinked) -> None:
        logger.info("Panel vinculado", extra={"extra_data": {"deviceId": event.device_id, "player": event.player_id}})

    def on_unlinked(event: PanelUnlinked) -> None:
        logger.info(
            "Panel desvinculado", extra={"extra_data": {"deviceId": event.device_id, "player": event.player_id}}
        )

    bus.subscribe(PanelAnnounced, on_announced)
    bus.subscribe(PanelLinked, on_linked)
    bus.subscribe(PanelUnlinked, on_unlinked)
