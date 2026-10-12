"""Único punto donde un error se convierte en respuesta HTTP.

Formato uniforme: { "error": { "code", "message", "details" } }
"""
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.errors import AppError
from app.shared.logger import get_logger

logger = get_logger()

_HTTP_CODES = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
_HTTP_MESSAGES = {404: "Ruta no encontrada", 405: "Método no permitido"}


def _body(code: str, message: str, details: object = None) -> dict:
    error: dict = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"error": error}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(_body(exc.code, exc.message, exc.details), status_code=exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        # FastAPI responde 422 por defecto; el equipo unificó en 400 (ADR-006).
        details = jsonable_encoder(exc.errors(), custom_encoder={Exception: str})
        return JSONResponse(_body("VALIDATION_ERROR", "Datos de entrada inválidos", details), status_code=400)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_CODES.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            _body(code, _HTTP_MESSAGES.get(exc.status_code, str(exc.detail))), status_code=exc.status_code
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        # Error inesperado: el detalle va al log; al cliente solo un mensaje genérico.
        logger.error(
            "Error no controlado",
            exc_info=exc,
            extra={"extra_data": {"error": str(exc)}},
        )
        return JSONResponse(_body("INTERNAL_ERROR", "Error interno del servidor"), status_code=500)
