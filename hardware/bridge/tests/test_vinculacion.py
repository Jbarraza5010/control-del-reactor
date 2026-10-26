"""Vinculación del panel desde el puente: anunciar, mostrar el código y reanunciar (PROTOCOL.md)."""
import json
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from reactor_bridge.__main__ import backend_base_url, build_parser, build_service, build_sink
from reactor_bridge.registrar import AnnounceResult, HttpRegistrar, parse_expires_at
from reactor_bridge.service import BridgeService
from reactor_bridge.sinks import HttpSink

NOW = datetime(2026, 10, 25, 15, 0, tzinfo=timezone.utc)


class FakeSource:
    def __init__(self, lines=()):
        self._lines = list(lines)

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


class FakeRegistrar:
    def __init__(self, *results):
        self.results = list(results)
        self.calls = []

    def announce(self, device_id, version):
        self.calls.append((device_id, version))
        return self.results.pop(0) if self.results else None


class Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def pending(code="482915", minutes=5):
    return AnnounceResult(linked=False, pairing_code=code, expires_at=NOW + timedelta(minutes=minutes))


def make(registrar, lines=("HELLO panel-01 1",), now=NOW):
    shown, clock = [], Clock()
    service = BridgeService(
        FakeSource(lines), FakeSink(), registrar=registrar, display=shown.append, monotonic=clock, utcnow=lambda: now
    )
    return service, shown, clock


def test_al_recibir_hello_anuncia_y_muestra_el_codigo():
    registrar = FakeRegistrar(pending("482915"))
    service, shown, _ = make(registrar)
    service.run()
    assert registrar.calls == [("panel-01", 1)]
    assert "482915" in shown[-1] and "panel-01" in shown[-1]


def test_panel_ya_vinculado_avisa_que_esta_listo():
    service, shown, _ = make(FakeRegistrar(AnnounceResult(linked=True, pairing_code=None, expires_at=None)))
    service.run()
    assert "ya vinculado" in shown[-1]


def test_si_el_backend_no_responde_avisa_y_sigue():
    service, shown, _ = make(FakeRegistrar(None))
    service.run()
    assert "No se pudo anunciar" in shown[-1]


def test_404_vuelve_a_anunciar_pero_no_en_rafaga():
    registrar = FakeRegistrar(pending("111111"), pending("222222"), pending("333333"))
    service, shown, clock = make(registrar)
    service.run()
    clock.t += 3
    service.on_rejected(404, {})
    service.on_rejected(404, {})  # inmediatamente después: se ignora
    assert len(registrar.calls) == 2
    assert "222222" in shown[-1]
    clock.t += 3
    service.on_rejected(404, {})
    assert len(registrar.calls) == 3


def test_409_con_codigo_vigente_recuerda_el_codigo_sin_pedir_otro():
    registrar = FakeRegistrar(pending("482915"))
    service, shown, clock = make(registrar)
    service.run()
    clock.t += 10
    service.on_rejected(409, {})
    assert len(registrar.calls) == 1
    assert shown[-1] == "Panel sin vincular: ingresa el código 482915 en el juego."
    service.on_rejected(409, {})  # el recordatorio no se repite en cada botón
    assert len([s for s in shown if "sin vincular" in s]) == 1


def test_409_con_codigo_vencido_pide_uno_nuevo():
    registrar = FakeRegistrar(pending("482915"), pending("777777"))
    service, shown, clock = make(registrar, now=NOW + timedelta(minutes=6))
    service.run()
    clock.t += 3
    service.on_rejected(409, {})
    assert len(registrar.calls) == 2 and "777777" in shown[-1]


def test_sin_registrar_modo_stdout_no_anuncia():
    service = BridgeService(FakeSource(["HELLO panel-01 1", "BTN UP press"]), FakeSink(), display=pytest.fail)
    service.run()
    assert service.device_id == "panel-01"


def test_device_id_forzado_se_usa_al_anunciar():
    registrar = FakeRegistrar(pending())
    service = BridgeService(
        FakeSource(["HELLO panel-01 1"]), FakeSink(), device_id="mesa-3", registrar=registrar, display=lambda _: None
    )
    service.run()
    assert registrar.calls == [("mesa-3", 1)]


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000",
        "http://localhost:8000/",
        "http://localhost:8000/api/v1/hardware",
        "http://localhost:8000/api/v1/hardware/events",
    ],
)
def test_backend_url_acepta_base_o_url_de_eventos(url):
    assert backend_base_url(url) == "http://localhost:8000"


def test_parse_expires_at_con_z():
    assert parse_expires_at("2026-10-13T18:05:00Z") == datetime(2026, 10, 13, 18, 5, tzinfo=timezone.utc)
    assert parse_expires_at(None) is None


# ---- Contra un servidor HTTP de verdad ------------------------------------------
class _Backend(BaseHTTPRequestHandler):
    routes: dict = {}
    received: list = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(length))
        _Backend.received.append((self.path, body))
        status, payload = _Backend.routes.get(self.path, (404, {"error": {"code": "NOT_FOUND", "message": "x"}}))
        data = json.dumps(payload).encode() if payload is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture
def backend():
    _Backend.routes, _Backend.received = {}, []
    server = HTTPServer(("127.0.0.1", 0), _Backend)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield server
    server.shutdown()


def test_http_registrar_envia_el_anuncio_y_lee_la_respuesta(backend):
    _Backend.routes["/api/v1/hardware/devices/announce"] = (
        200,
        {"deviceId": "panel-01", "linked": False, "pairingCode": "482915", "expiresAt": "2026-10-13T18:05:00Z"},
    )
    url = f"http://127.0.0.1:{backend.server_port}/api/v1/hardware/devices/announce"
    result = HttpRegistrar(url).announce("panel-01", 1)
    assert result == AnnounceResult(False, "482915", datetime(2026, 10, 13, 18, 5, tzinfo=timezone.utc))
    assert _Backend.received == [("/api/v1/hardware/devices/announce", {"deviceId": "panel-01", "version": 1})]


def test_http_registrar_devuelve_none_si_hay_error(backend):
    url = f"http://127.0.0.1:{backend.server_port}/no-existe"
    assert HttpRegistrar(url).announce("panel-01", 1) is None
    assert HttpRegistrar("http://127.0.0.1:9/x", timeout_seconds=0.2).announce("panel-01", 1) is None


def test_http_sink_avisa_los_rechazos_con_su_codigo(backend):
    _Backend.routes["/api/v1/hardware/events"] = (409, {"error": {"code": "CONFLICT", "message": "x"}})
    rejected = []
    sink = HttpSink(f"http://127.0.0.1:{backend.server_port}/api/v1/hardware/events", on_rejected=lambda s, m: rejected.append((s, m)))
    sink.send({"n": 1})
    sink.close()
    assert rejected == [(409, {"n": 1})]


def test_cableado_completo_404_provoca_reanuncio(backend):
    """main(): el HttpSink avisa el 404 al servicio, que vuelve a anunciar el panel."""
    _Backend.routes["/api/v1/hardware/devices/announce"] = (
        200,
        {"deviceId": "panel-01", "linked": False, "pairingCode": "123456", "expiresAt": "2099-01-01T00:00:00Z"},
    )
    args = build_parser().parse_args(["--backend-url", f"http://127.0.0.1:{backend.server_port}"])
    sink = build_sink(args)
    service = build_service(args, FakeSource(), sink)
    service.handle_line("HELLO panel-01 1")  # anuncio 1
    service._last_announce = -100  # simula que pasó el tiempo mínimo entre anuncios
    service.handle_line("BTN UP press")  # /events responde 404 -> anuncio 2
    sink.close()
    paths = [p for p, _ in _Backend.received]
    assert paths == [
        "/api/v1/hardware/devices/announce",
        "/api/v1/hardware/events",
        "/api/v1/hardware/devices/announce",
    ]
