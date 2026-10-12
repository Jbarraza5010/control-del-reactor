"""Jerarquía de errores de la aplicación.

Las capas internas lanzan estos errores; solo los manejadores HTTP los traducen a respuestas.
"""
from typing import Any


class AppError(Exception):
    def __init__(self, code: str, message: str, http_status: int, details: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details


class ValidationAppError(AppError):
    def __init__(self, message: str = "Datos de entrada inválidos", details: Any = None) -> None:
        super().__init__("VALIDATION_ERROR", message, 400, details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Credenciales inválidas") -> None:
        super().__init__("UNAUTHORIZED", message, 401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Acción no permitida") -> None:
        super().__init__("FORBIDDEN", message, 403)


class NotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado") -> None:
        super().__init__("NOT_FOUND", message, 404)


class ConflictError(AppError):
    def __init__(self, message: str = "El recurso ya existe") -> None:
        super().__init__("CONFLICT", message, 409)


class NotImplementedAppError(AppError):
    def __init__(self, message: str = "Endpoint pendiente de implementar") -> None:
        super().__init__("NOT_IMPLEMENTED", message, 501)
