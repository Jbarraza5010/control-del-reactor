import pytest

from reactor_bridge.protocol import ButtonEvent, Hello, ProtocolError, build_message, parse_line


def test_parsea_hello():
    assert parse_line("HELLO panel-01 1") == Hello(device_id="panel-01", version=1)


@pytest.mark.parametrize("button", ["UP", "DOWN", "LEFT", "RIGHT", "ACTION"])
@pytest.mark.parametrize("event", ["press", "release"])
def test_parsea_todos_los_botones(button, event):
    assert parse_line(f"BTN {button} {event}") == ButtonEvent(button=button, event=event)


def test_tolera_espacios_y_retorno_de_carro():
    assert parse_line("  BTN UP press\r\n") == ButtonEvent(button="UP", event="press")


@pytest.mark.parametrize(
    "line",
    [
        "",
        "   ",
        "HOLA mundo",
        "BTN",
        "BTN UP",
        "BTN JUMP press",
        "BTN UP hold",
        "BTN UP press extra",
        "HELLO",
        "HELLO panel-01",
        "HELLO panel 01 1",
        "HELLO panel-01 abc",
        "HELLO panel-01 99",
        "HELLO pánel 1",
    ],
)
def test_rechaza_lineas_invalidas(line):
    with pytest.raises(ProtocolError):
        parse_line(line)


def test_arma_el_mensaje_de_protocol_md():
    message = build_message("panel-01", ButtonEvent("ACTION", "press"), 1760000000000)
    assert message == {
        "deviceId": "panel-01",
        "button": "ACTION",
        "event": "press",
        "timestamp": 1760000000000,
    }
