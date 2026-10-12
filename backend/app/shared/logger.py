"""Logger mínimo con salida JSON. Se puede reemplazar sin tocar el resto del código."""
import json
import logging
import sys
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "level": record.levelname.lower(),
            "time": datetime.now(timezone.utc).isoformat(),
            "message": record.getMessage(),
        }
        data.update(getattr(record, "extra_data", {}))
        if record.exc_info:
            data["stack"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False, default=str)


def get_logger(name: str = "reactor") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger
