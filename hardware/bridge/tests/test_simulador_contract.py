"""El simulador debe emitir exactamente lo que entiende el puente (mismo contrato que el Arduino)."""
from simulador import DEMO_SEQUENCE, KEY_TO_BUTTON, hello_line, run_keys
from reactor_bridge.protocol import BUTTONS, ButtonEvent, Hello, parse_line


def test_hello_del_simulador_es_valido_para_el_puente():
    assert parse_line(hello_line("panel-sim-01")) == Hello(device_id="panel-sim-01", version=1)


def test_todas_las_teclas_mapean_a_botones_del_protocolo():
    assert set(KEY_TO_BUTTON.values()) <= BUTTONS
    assert set(KEY_TO_BUTTON.values()) == BUTTONS


def test_secuencia_demo_genera_pares_press_release_validos():
    emitted = []
    run_keys(DEMO_SEQUENCE, emitted.append, sleep=lambda _s: None)
    events = [parse_line(line) for line in emitted]
    assert all(isinstance(e, ButtonEvent) for e in events)
    assert len(events) == 2 * len(DEMO_SEQUENCE)
    assert [e.event for e in events] == ["press", "release"] * len(DEMO_SEQUENCE)


def test_tecla_desconocida_se_ignora():
    emitted = []
    run_keys(["z", "w"], emitted.append, sleep=lambda _s: None)
    assert emitted == ["BTN UP press", "BTN UP release"]
