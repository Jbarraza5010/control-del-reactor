import io
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from reactor_bridge.sinks import HttpSink, StdoutSink
from reactor_bridge.sources import SerialSource, StdinSource


def test_stdin_source_omite_lineas_vacias():
    source = StdinSource(io.StringIO("HELLO panel-01 1\n\n  \nBTN UP press\n"))
    assert list(source.lines()) == ["HELLO panel-01 1", "BTN UP press"]


def test_stdout_sink_imprime_json_compacto():
    out = io.StringIO()
    StdoutSink(out).send({"deviceId": "p", "button": "UP", "event": "press", "timestamp": 1})
    assert json.loads(out.getvalue()) == {"deviceId": "p", "button": "UP", "event": "press", "timestamp": 1}
    assert out.getvalue().endswith("\n")


class _RecordingHandler(BaseHTTPRequestHandler):
    received: list = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        _RecordingHandler.received.append((self.headers["Content-Type"], json.loads(self.rfile.read(length))))
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass


def test_http_sink_envia_post_json_en_orden():
    _RecordingHandler.received = []
    server = HTTPServer(("127.0.0.1", 0), _RecordingHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    sink = HttpSink(f"http://127.0.0.1:{server.server_port}/eventos")
    try:
        sink.send({"n": 1})
        sink.send({"n": 2})
        sink.close()  # vacía la cola antes de terminar
    finally:
        server.shutdown()
    assert _RecordingHandler.received == [("application/json", {"n": 1}), ("application/json", {"n": 2})]


def test_http_sink_sobrevive_si_el_backend_no_responde():
    sink = HttpSink("http://127.0.0.1:9/eventos", timeout_seconds=0.2)  # puerto sin servicio
    sink.send({"n": 1})
    sink.send({"n": 2})
    sink.close()  # no debe lanzar ni quedarse colgado


class _FakeSerial:
    def __init__(self, chunks):
        self._chunks = list(chunks)
        self.written = []
        self.closed = False

    def readline(self):
        if not self._chunks:
            raise OSError("cable desconectado")
        return self._chunks.pop(0)

    def write(self, data):
        self.written.append(data)

    def close(self):
        self.closed = True


def test_serial_source_lee_pide_hello_y_se_reconecta():
    first = _FakeSerial([b"HELLO panel-01 1\r\n", b"", b"BTN UP press\n"])
    second = _FakeSerial([b"BTN UP release\n"])
    connections = iter([first, second])
    source = SerialSource(
        port="/dev/ttyACM0",
        reconnect_seconds=0,
        serial_factory=lambda *args, **kwargs: next(connections),
    )
    received = []
    for line in source.lines():
        received.append(line)
        if len(received) == 3:
            source.close()
            break
    assert received == ["HELLO panel-01 1", "BTN UP press", "BTN UP release"]
    assert first.written == [b"WHO\n"] and first.closed
    assert second.written == [b"WHO\n"]
