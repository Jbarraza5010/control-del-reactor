from fastapi import FastAPI

from app.config import get_settings
from app.container import Container, build_container
from app.presentation.api.error_handlers import register_error_handlers
from app.presentation.api.routes import auth, health


def create_app(container: Container | None = None) -> FastAPI:
    """Fábrica de la aplicación. En pruebas se le pasa un Container con piezas falsas."""
    app = FastAPI(title="Control del Reactor - API de cuentas", version="0.2.0")
    app.state.container = container or build_container(get_settings())
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    return app
