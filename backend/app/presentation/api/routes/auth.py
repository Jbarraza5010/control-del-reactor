"""Rutas de la API de cuentas (Sprint 2):
- US-001/002/003 -> POST /api/v1/auth/register
- US-004         -> POST /api/v1/auth/verify-email
- US-005         -> POST /api/v1/auth/login
- US-007         -> POST /api/v1/auth/forgot-password y POST /api/v1/auth/reset-password
"""
from fastapi import APIRouter, Depends
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.container import Container
from app.domain.entities.user import User
from app.presentation.api.dependencies import get_container

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class _AuthModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class RegisterRequest(_AuthModel):
    username: str = Field(
        validation_alias=AliasChoices("username", "usuario"),
        examples=["ReactorPlayer"],
    )
    email: str = Field(
        validation_alias=AliasChoices("email", "correo"),
        examples=["jugador@tec.ac.cr"],
    )
    password: str = Field(
        validation_alias=AliasChoices("password", "clave", "contrasena"),
        examples=["Reactor1234"],
    )


class VerifyEmailRequest(_AuthModel):
    code: str = Field(
        validation_alias=AliasChoices("code", "token", "codigo"),
        examples=["123456"],
    )
    email: str | None = Field(
        default=None,
        validation_alias=AliasChoices("email", "correo"),
        examples=["jugador@tec.ac.cr"],
    )


class LoginRequest(_AuthModel):
    email: str = Field(
        validation_alias=AliasChoices("email", "correo"),
        examples=["jugador@tec.ac.cr"],
    )
    password: str = Field(
        validation_alias=AliasChoices("password", "clave", "contrasena"),
        examples=["Reactor1234"],
    )


class ForgotPasswordRequest(_AuthModel):
    email: str = Field(
        validation_alias=AliasChoices("email", "correo"),
        examples=["jugador@tec.ac.cr"],
    )


class ResetPasswordRequest(_AuthModel):
    code: str = Field(
        validation_alias=AliasChoices("code", "token", "codigo"),
        examples=["123456"],
    )
    new_password: str = Field(
        validation_alias=AliasChoices(
            "new_password",
            "newPassword",
            "password",
            "clave",
            "contrasena",
            "nueva_contrasena",
            "nueva_clave",
        ),
        examples=["NuevaClave123"],
    )
    email: str | None = Field(
        default=None,
        validation_alias=AliasChoices("email", "correo"),
        examples=["jugador@tec.ac.cr"],
    )


class UserResponse(_AuthModel):
    id: str
    username: str
    email: str
    status: str
    message: str


class UserSummary(_AuthModel):
    id: str
    username: str
    email: str
    status: str


class LoginResponse(_AuthModel):
    token: str
    user: UserSummary
    message: str


class MessageResponse(_AuthModel):
    message: str


def _user_response(user: User, message: str) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        status=user.status,
        message=message,
    )


@router.post(
    "/register",
    status_code=201,
    response_model=UserResponse,
    summary="Registrar cuenta (US-001, US-002, US-003)",
)
def register(
    body: RegisterRequest,
    container: Container = Depends(get_container),
) -> UserResponse:
    user = container.auth_service.register(body.username, body.email, body.password)
    return _user_response(
        user,
        "Cuenta creada exitosamente. Revisa tu correo para obtener el código de verificación.",
    )


@router.post(
    "/verify-email",
    status_code=200,
    response_model=UserResponse,
    summary="Verificar correo (US-004)",
)
def verify_email(
    body: VerifyEmailRequest,
    container: Container = Depends(get_container),
) -> UserResponse:
    user = container.auth_service.verify_email(body.code, body.email)
    return _user_response(user, "Se ha validado el correo exitosamente.")


@router.post(
    "/login",
    status_code=200,
    response_model=LoginResponse,
    summary="Iniciar sesión (US-005)",
)
def login(
    body: LoginRequest,
    container: Container = Depends(get_container),
) -> LoginResponse:
    result = container.auth_service.login(body.email, body.password)
    return LoginResponse(
        token=result.token,
        user=UserSummary(
            id=result.user.id,
            username=result.user.username,
            email=result.user.email,
            status=result.user.status,
        ),
        message="Inicio de sesión exitoso.",
    )


@router.post(
    "/forgot-password",
    status_code=200,
    response_model=MessageResponse,
    summary="Solicitar recuperación de contraseña (US-007)",
)
def forgot_password(
    body: ForgotPasswordRequest,
    container: Container = Depends(get_container),
) -> MessageResponse:
    container.auth_service.forgot_password(body.email)
    return MessageResponse(message="Se ha enviado un código de un solo uso al correo.")


@router.post(
    "/reset-password",
    status_code=200,
    response_model=MessageResponse,
    summary="Restablecer contraseña (US-007)",
)
def reset_password(
    body: ResetPasswordRequest,
    container: Container = Depends(get_container),
) -> MessageResponse:
    container.auth_service.reset_password(body.code, body.new_password, body.email)
    return MessageResponse(message="Contraseña actualizada exitosamente.")
