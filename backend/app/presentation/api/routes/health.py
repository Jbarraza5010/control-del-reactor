from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.container import Container
from app.presentation.api.dependencies import get_container

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def liveness() -> dict:
    """Liveness: el proceso está vivo. Lo usa Docker (HEALTHCHECK) y el CI."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/db")
def readiness(container: Container = Depends(get_container)) -> JSONResponse:
    """Readiness: además verifica la conexión con PostgreSQL."""
    try:
        container.database_health.ping()
    except Exception:  # noqa: BLE001 - cualquier fallo significa "base caída"
        return JSONResponse({"status": "degraded", "database": "down"}, status_code=503)
    return JSONResponse({"status": "ok", "database": "up"})
