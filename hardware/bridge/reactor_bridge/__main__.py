"""Punto de entrada: python -m reactor_bridge [opciones]"""
import argparse
import logging
import os
import sys

from reactor_bridge.service import BridgeService
from reactor_bridge.sinks import EventSink, HttpSink, StdoutSink
from reactor_bridge.sources import LineSource, SerialSource, StdinSource

# Ruta definida en hardware/PROTOCOL.md ("Rutas del backend"); el backend aún no la implementa.
DEFAULT_BACKEND_URL = "http://localhost:8000/api/v1/hardware/events"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="reactor_bridge", description="Puente USB serial del panel de Control del Reactor")
    parser.add_argument("--source", choices=["serial", "stdin"], default="serial",
                        help="serial: Arduino por USB; stdin: líneas del simulador (por defecto: serial)")
    parser.add_argument("--port", default=os.environ.get("HARDWARE_SERIAL_PORT", "auto"),
                        help="Puerto serial (ej. /dev/ttyACM0, COM3) o 'auto' para detectarlo")
    parser.add_argument("--baud", type=int, default=int(os.environ.get("HARDWARE_BAUD", "9600")))
    parser.add_argument("--sink", choices=["http", "stdout"], default="http",
                        help="http: enviar al backend; stdout: imprimir el JSON (por defecto: http)")
    parser.add_argument("--backend-url", default=os.environ.get("HARDWARE_BACKEND_URL", DEFAULT_BACKEND_URL))
    parser.add_argument("--device-id", default=os.environ.get("HARDWARE_DEVICE_ID"),
                        help="Forzar el deviceId en lugar del que anuncia el Arduino")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser


def build_source(args: argparse.Namespace) -> LineSource:
    if args.source == "stdin":
        return StdinSource()
    return SerialSource(port=args.port, baud=args.baud)


def build_sink(args: argparse.Namespace) -> EventSink:
    if args.sink == "stdout":
        return StdoutSink()
    return HttpSink(args.backend_url)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Los logs van a stderr para no mezclarse con el JSON que imprime el sink stdout.
    logging.basicConfig(level=args.log_level, stream=sys.stderr, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    source = build_source(args)
    sink = build_sink(args)
    service = BridgeService(source, sink, device_id=args.device_id)
    try:
        service.run()
    except KeyboardInterrupt:
        logging.getLogger("reactor_bridge").info("Detenido por el usuario")
    finally:
        source.close()
        sink.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
