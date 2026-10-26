import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).resolve().parents[1]
SIMULATOR_DIR = BRIDGE_DIR.parent / "simulador"

for path in (BRIDGE_DIR, SIMULATOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
