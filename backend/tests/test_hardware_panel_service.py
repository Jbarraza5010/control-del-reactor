"""Reglas de vinculación del panel físico (US-013, hardware/PROTOCOL.md)."""
from datetime import datetime, timedelta, timezone

import pytest

from app.application.services.hardware_panel_service import HardwarePanelService
from app.infrastructure.persistence.memory.in_memory_hardware_panel_repository import (
    InMemoryHardwarePanelRepository,
)
from app.shared.errors import ConflictError, NotFoundError, ValidationAppError
from app.shared.events import EventBus, HardwareButtonEvent, PanelAnnounced, PanelLinked, PanelUnlinked

T0 = datetime(2026, 10, 25, 15, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


def codes(*values):
    it = iter(values)
    return lambda: next(it)


def make(code_generator=None):
    bus, clock, events = EventBus(), Clock(), []
    for kind in (PanelAnnounced, PanelLinked, PanelUnlinked, HardwareButtonEvent):
        bus.subscribe(kind, events.append)
    service = HardwarePanelService(
        InMemoryHardwarePanelRepository(), bus, clock=clock, code_generator=code_generator or codes("111111", "222222", "333333")
    )
    return service, clock, events


def test_anunciar_un_panel_nuevo_genera_codigo_de_6_digitos_que_vence_en_5_minutos():
    service, _, events = make()
    panel = service.announce("panel-01", 1)
    assert panel.pairing_code == "111111"
    assert panel.pairing_expires_at == T0 + timedelta(minutes=5)
    assert not panel.is_linked
    assert events == [PanelAnnounced(device_id="panel-01", pairing_code="111111")]


def test_el_codigo_aleatorio_por_defecto_tiene_6_digitos():
    service = HardwarePanelService(InMemoryHardwarePanelRepository(), EventBus())
    code = service.announce("panel-01", 1).pairing_code
    assert len(code) == 6 and code.isdigit()


def test_reanunciar_sin_vincular_invalida_el_codigo_anterior():
    service, _, _ = make()
    service.announce("panel-01", 1)
    assert service.announce("panel-01", 1).pairing_code == "222222"
    with pytest.raises(NotFoundError):
        service.link("jugador-1", "111111")
    assert service.link("jugador-1", "222222").device_id == "panel-01"


def test_vincular_asocia_el_panel_al_jugador_y_el_codigo_es_de_un_solo_uso():
    service, _, events = make()
    service.announce("panel-01", 1)
    panel = service.link("jugador-1", "111111")
    assert panel.player_id == "jugador-1" and panel.linked_at == T0
    assert PanelLinked(device_id="panel-01", player_id="jugador-1") in events
    with pytest.raises(NotFoundError):
        service.link("jugador-2", "111111")


def test_codigo_vencido_no_sirve():
    service, clock, _ = make()
    service.announce("panel-01", 1)
    clock.now = T0 + timedelta(minutes=5)
    with pytest.raises(NotFoundError):
        service.link("jugador-1", "111111")


@pytest.mark.parametrize("bad", ["12345", "1234567", "abcdef", ""])
def test_codigo_con_formato_invalido_es_error_de_validacion(bad):
    service, _, _ = make()
    with pytest.raises(ValidationAppError):
        service.link("jugador-1", bad)


def test_un_jugador_no_puede_tener_dos_paneles():
    service, _, _ = make()
    service.announce("panel-01", 1)
    service.announce("panel-02", 1)
    service.link("jugador-1", "111111")
    with pytest.raises(ConflictError):
        service.link("jugador-1", "222222")


def test_panel_vinculado_que_se_reanuncia_conserva_el_vinculo_sin_codigo():
    service, _, _ = make()
    service.announce("panel-01", 1)
    service.link("jugador-1", "111111")
    panel = service.announce("panel-01", 1)
    assert panel.is_linked and panel.pairing_code is None and panel.player_id == "jugador-1"


def test_version_de_protocolo_no_soportada():
    service, _, _ = make()
    with pytest.raises(ValidationAppError):
        service.announce("panel-01", 2)


def test_device_id_invalido():
    service, _, _ = make()
    with pytest.raises(ValidationAppError):
        service.announce("panel con espacios", 1)


def test_boton_de_panel_vinculado_se_publica_con_el_jugador():
    service, _, events = make()
    service.announce("panel-01", 1)
    service.link("jugador-1", "111111")
    service.handle_button("panel-01", "UP", "press", 1760000000000)
    assert events[-1] == HardwareButtonEvent(
        device_id="panel-01", player_id="jugador-1", button="UP", event="press", timestamp=1760000000000
    )


def test_boton_de_panel_no_anunciado_es_404_y_de_panel_sin_vincular_es_409():
    service, _, _ = make()
    with pytest.raises(NotFoundError):
        service.handle_button("panel-01", "UP", "press", 1)
    service.announce("panel-01", 1)
    with pytest.raises(ConflictError):
        service.handle_button("panel-01", "UP", "press", 1)


def test_boton_o_evento_desconocido():
    service, _, _ = make()
    with pytest.raises(ValidationAppError):
        service.handle_button("panel-01", "JUMP", "press", 1)
    with pytest.raises(ValidationAppError):
        service.handle_button("panel-01", "UP", "hold", 1)


def test_desvincular_olvida_el_panel_y_debe_anunciarse_de_nuevo():
    service, _, events = make()
    service.announce("panel-01", 1)
    service.link("jugador-1", "111111")
    service.unlink("jugador-1")
    assert events[-1] == PanelUnlinked(device_id="panel-01", player_id="jugador-1")
    with pytest.raises(NotFoundError):
        service.get_link("jugador-1")
    with pytest.raises(NotFoundError):
        service.handle_button("panel-01", "UP", "press", 1)  # el puente reanunciará
    assert service.announce("panel-01", 1).pairing_code == "222222"


def test_desvincular_sin_panel_es_404():
    service, _, _ = make()
    with pytest.raises(NotFoundError):
        service.unlink("jugador-1")


def test_no_repite_un_codigo_que_ya_tiene_otro_panel():
    service, _, _ = make(codes("111111", "111111", "444444"))
    service.announce("panel-01", 1)
    assert service.announce("panel-02", 1).pairing_code == "444444"
