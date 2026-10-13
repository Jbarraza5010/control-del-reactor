"""Simulador del panel. Uso:

    python simulador.py --interactive | PYTHONPATH=../bridge python -m reactor_bridge --source stdin
    python simulador.py --demo        | PYTHONPATH=../bridge python -m reactor_bridge --source stdin --sink stdout

Los mensajes de ayuda salen por stderr; por stdout (o --output) salen solo las líneas del protocolo.
"""
import argparse
import sys
import time
from collections.abc import Callable, Iterable
from typing import IO

# ---- Formato de las líneas (idéntico al firmware del Arduino) ----
PROTOCOL_VERSION = 1

# Teclas del modo interactivo -> código de botón del protocolo.
KEY_TO_BUTTON = {
    "w": "UP",
    "s": "DOWN",
    "a": "LEFT",
    "d": "RIGHT",
    "e": "ACTION",
    "x": "ACTION",
    "up": "UP",
    "down": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "action": "ACTION",
}


def hello_line(device_id: str) -> str:
    return f"HELLO {device_id} {PROTOCOL_VERSION}"


def button_line(button: str, event: str) -> str:
    return f"BTN {button} {event}"


# ---- Simulador ----
DEMO_SEQUENCE = ["d", "d", "s", "s", "a", "e", "w", "e"]


def tap(emit: Callable[[str], None], button: str, hold_seconds: float, sleep: Callable[[float], None] = time.sleep) -> None:
    """Presiona y suelta un botón."""
    emit(button_line(button, "press"))
    sleep(hold_seconds)
    emit(button_line(button, "release"))


def run_keys(
    keys: Iterable[str],
    emit: Callable[[str], None],
    hold_seconds: float = 0.08,
    gap_seconds: float = 0.12,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    for key in keys:
        button = KEY_TO_BUTTON.get(key.lower())
        if button is None:
            print(f"Tecla ignorada: {key!r} (usa w a s d e)", file=sys.stderr)
            continue
        tap(emit, button, hold_seconds, sleep)
        sleep(gap_seconds)


def run_interactive(emit: Callable[[str], None], stdin: IO[str], hold_seconds: float) -> None:
    print("Simulador del panel. Escribe teclas y Enter: w=ARRIBA s=ABAJO a=IZQUIERDA d=DERECHA e=ACCION. Ctrl+D para salir.",
          file=sys.stderr)
    for text in stdin:
        run_keys(text.split(), emit, hold_seconds)


def run_demo(emit: Callable[[str], None], hold_seconds: float, repeat: bool) -> None:
    while True:
        run_keys(DEMO_SEQUENCE, emit, hold_seconds, gap_seconds=0.4)
        if not repeat:
            return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="simulador", description="Simulador del panel de 5 botones")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--interactive", action="store_true", help="Leer teclas del teclado (w a s d e)")
    mode.add_argument("--demo", action="store_true", help="Reproducir una secuencia de botones de ejemplo")
    parser.add_argument("--device-id", default="panel-sim-01")
    parser.add_argument("--hold-ms", type=int, default=80, help="Tiempo entre press y release")
    parser.add_argument("--repeat", action="store_true", help="Con --demo, repetir la secuencia sin parar")
    parser.add_argument("--output", help="Archivo o puerto virtual donde escribir (por defecto: stdout)")
    args = parser.parse_args(argv)

    stream = open(args.output, "w", encoding="ascii") if args.output else sys.stdout

    def emit(line: str) -> None:
        stream.write(line + "\n")
        stream.flush()

    hold_seconds = args.hold_ms / 1000
    try:
        emit(hello_line(args.device_id))
        if args.interactive:
            run_interactive(emit, sys.stdin, hold_seconds)
        else:
            run_demo(emit, hold_seconds, args.repeat)
    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        if args.output:
            stream.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
