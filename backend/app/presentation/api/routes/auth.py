"""Contrato inicial de la API de cuentas (Sprint 2).

Todos los endpoints responden 501 hasta que Moisés los implemente:
  US-001/002/003 -> register      US-004 -> verify-email
  US-005 -> login                 US-007 -> forgot-password / reset-password
Al implementarlos: declarar el cuerpo con modelos pydantic, llamar a un servicio de
application/ y lanzar subclases de AppError. El contrato se ve en http://localhost:8000/docs
"""
from fastapi import APIRouter

from app.shared.errors import NotImplementedAppError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", summary="Registrar cuenta (US-001, US-002, US-003)")
def register() -> None:
    raise NotImplementedAppError()


@router.post("/verify-email", summary="Verificar correo (US-004)")
def verify_email() -> None:
    raise NotImplementedAppError()


@router.post("/login", summary="Iniciar sesión (US-005)")
def login() -> None:
    raise NotImplementedAppError()


@router.post("/forgot-password", summary="Solicitar recuperación de contraseña (US-007)")
def forgot_password() -> None:
    raise NotImplementedAppError()


@router.post("/reset-password", summary="Restablecer contraseña (US-007)")
def reset_password() -> None:
    raise NotImplementedAppError()
