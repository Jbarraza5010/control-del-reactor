from fastapi import FastAPI

from app.config import get_settings
from app.container import Container, build_container
from app.presentation.api.error_handlers import register_error_handlers
from app.presentation.api.hardware_hub import HardwareHub
from app.presentation.api.routes import auth, hardware, health


def create_app(container: Container | None = None) -> FastAPI:
    """Fábrica de la aplicación. En pruebas se le pasa un Container con piezas falsas."""
    app = FastAPI(title="Control del Reactor - API de cuentas", version="0.2.0")
    app.state.container = container or build_container(get_settings())
    # El hub escucha los eventos del panel en el EventBus y los reenvía por WebSocket.
    app.state.hardware_hub = HardwareHub(app.state.container.event_bus)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(hardware.router)
    return app
