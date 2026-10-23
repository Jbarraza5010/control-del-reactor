from reactor_bridge.service import BridgeService


class FakeSource:
    def __init__(self, lines):
        self._lines = lines

    def lines(self):
        yield from self._lines

    def request_hello(self):
        pass

    def close(self):
        pass


class FakeSink:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)

    def close(self):
        pass


def make_service(lines, device_id=None, ticks=None):
    sink = FakeSink()
    clock = iter(ticks or range(1000, 2000))
    service = BridgeService(FakeSource(lines), sink, clock_ms=lambda: next(clock), device_id=device_id)
    return service, sink


def test_reenvia_los_botones_con_el_device_id_anunciado():
    service, sink = make_service(["HELLO panel-07 1", "BTN UP press", "BTN UP release"])
    service.run()
    assert sink.messages == [
        {"deviceId": "panel-07", "button": "UP", "event": "press", "timestamp": 1001},
        {"deviceId": "panel-07", "button": "UP", "event": "release", "timestamp": 1002},
    ]


def test_descarta_botones_antes_del_hello():
    service, sink = make_service(["BTN UP press", "HELLO panel-01 1", "BTN UP release"])
    service.run()
    assert [m["event"] for m in sink.messages] == ["release"]


def test_lineas_invalidas_no_detienen_el_puente():
    service, sink = make_service(["HELLO panel-01 1", "ruido###", "BTN XYZ press", "BTN DOWN press"])
    service.run()
    assert len(sink.messages) == 1
    assert sink.messages[0]["button"] == "DOWN"


def test_device_id_forzado_ignora_el_hello():
    service, sink = make_service(["HELLO panel-01 1", "BTN LEFT press"], device_id="mesa-3")
    service.run()
    assert sink.messages[0]["deviceId"] == "mesa-3"
    assert service.device_id == "mesa-3"


def test_el_timestamp_lo_pone_el_puente_al_recibir_la_linea():
    service, sink = make_service(["HELLO panel-01 1", "BTN ACTION press"], ticks=[10, 55])
    service.run()
    assert sink.messages[0]["timestamp"] == 55
