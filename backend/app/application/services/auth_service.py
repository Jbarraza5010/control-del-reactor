"""Casos de uso de cuentas (Sprint 2):
- US-001, US-002, US-003: Registro de cuenta con validación de formato y duplicados.
- US-004: Verificación de correo electrónico con código de un solo uso.
- US-005: Inicio de sesión y emisión de token de sesión.
- US-007: Recuperación y restablecimiento de contraseña con revocación de sesiones.
- US-008: Consulta de perfil y estadísticas del jugador autenticado.
"""
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
import secrets
from uuid import uuid4

from app.domain.entities.auth_token import AuthToken
from app.domain.entities.player_profile import PlayerProfile
from app.domain.entities.user import User
from app.domain.repositories.auth_token_repository import AuthTokenRepository
from app.domain.repositories.user_repository import UserRepository
from app.shared.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationAppError,
)
from app.shared.events import EventBus, PasswordResetRequested, UserRegistered

VERIFY_TOKEN_TTL = timedelta(hours=24)
RESET_TOKEN_TTL = timedelta(hours=1)
SESSION_TOKEN_TTL = timedelta(days=7)

_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
_LETTER_RE = re.compile(r"[A-Za-z]")
_DIGIT_RE = re.compile(r"[0-9]")

_PBKDF2_ITERATIONS = 120_000


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _random_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _random_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    try:
        iterations = int(parts[1])
    except ValueError:
        return False
    salt = parts[2]
    expected_hex = parts[3]
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return hmac.compare_digest(derived.hex(), expected_hex)


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: User


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: AuthTokenRepository,
        event_bus: EventBus,
        clock: Callable[[], datetime] = _utcnow,
        code_generator: Callable[[], str] = _random_code,
        session_token_generator: Callable[[], str] = _random_session_token,
    ) -> None:
        self._users = user_repository
        self._tokens = token_repository
        self._bus = event_bus
        self._clock = clock
        self._code_generator = code_generator
        self._session_token_generator = session_token_generator

    def register(self, username: str, email: str, password: str) -> User:
        clean_username = username.strip()
        clean_email = email.strip().lower()
        self._validate_username(clean_username)
        self._validate_email(clean_email)
        self._validate_password(password)

        if self._users.find_by_username(clean_username) is not None:
            raise ConflictError("El nombre de usuario ya está en uso")
        if self._users.find_by_email(clean_email) is not None:
            raise ConflictError("El correo electrónico ya está registrado")

        now = self._clock()
        user = User(
            id=str(uuid4()),
            username=clean_username,
            email=clean_email,
            password_hash=hash_password(password),
            status="PENDIENTE_VERIFICACION",
            created_at=now,
        )
        user = self._users.save(user)

        self._tokens.delete_by_user_and_purpose(user.id, "verify")
        raw_code, digest = self._new_unique_code()
        self._tokens.save(
            AuthToken(
                digest=digest,
                user_id=user.id,
                purpose="verify",
                expires_at=now + VERIFY_TOKEN_TTL,
            )
        )
        self._bus.publish(UserRegistered(user_id=user.id, email=user.email, verification_token=raw_code))
        return user

    def verify_email(self, code: str, email: str | None = None) -> User:
        clean_code = code.strip()
        if not clean_code:
            raise ValidationAppError("Ingrese el código de verificación")

        now = self._clock()
        digest = hash_token(clean_code)
        stored_token = self._tokens.find_by_digest(digest)
        if stored_token is None or stored_token.purpose != "verify":
            raise ValidationAppError("Código de verificación inválido o expirado")
        if stored_token.is_expired(now):
            self._tokens.delete_by_digest(digest)
            raise ValidationAppError("Código de verificación inválido o expirado")

        user = self._users.find_by_id(stored_token.user_id)
        if user is None:
            self._tokens.delete_by_digest(digest)
            raise NotFoundError("Usuario no encontrado")

        if email is not None and email.strip():
            if user.email.lower() != email.strip().lower():
                raise ValidationAppError("Código de verificación inválido o expirado")

        user.status = "ACTIVA"
        user = self._users.save(user)
        self._tokens.delete_by_digest(digest)
        return user

    def login(self, email: str, password: str) -> LoginResult:
        clean_email = email.strip().lower()
        if not clean_email or not password:
            raise ValidationAppError("Ingrese su correo y contraseña")

        user = self._users.find_by_email(clean_email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Correo o contraseña incorrecta")

        if user.status != "ACTIVA":
            raise ForbiddenError("Debes verificar tu correo electrónico antes de iniciar sesión")

        now = self._clock()
        raw_token = self._session_token_generator()
        self._tokens.save(
            AuthToken(
                digest=hash_token(raw_token),
                user_id=user.id,
                purpose="session",
                expires_at=now + SESSION_TOKEN_TTL,
            )
        )
        return LoginResult(token=raw_token, user=user)

    def forgot_password(self, email: str) -> None:
        clean_email = email.strip().lower()
        self._validate_email(clean_email)

        user = self._users.find_by_email(clean_email)
        if user is None:
            raise NotFoundError("No existe una cuenta registrada con ese correo")

        now = self._clock()
        self._tokens.delete_by_user_and_purpose(user.id, "reset")
        raw_code, digest = self._new_unique_code()
        self._tokens.save(
            AuthToken(
                digest=digest,
                user_id=user.id,
                purpose="reset",
                expires_at=now + RESET_TOKEN_TTL,
            )
        )
        self._bus.publish(PasswordResetRequested(user_id=user.id, email=user.email, reset_token=raw_code))

    def reset_password(self, code: str, new_password: str, email: str | None = None) -> User:
        clean_code = code.strip()
        if not clean_code:
            raise ValidationAppError("Ingrese el código de un solo uso")
        self._validate_password(new_password)

        now = self._clock()
        digest = hash_token(clean_code)
        stored_token = self._tokens.find_by_digest(digest)
        if stored_token is None or stored_token.purpose != "reset":
            raise ValidationAppError("Código de recuperación inválido o expirado")
        if stored_token.is_expired(now):
            self._tokens.delete_by_digest(digest)
            raise ValidationAppError("Código de recuperación inválido o expirado")

        user = self._users.find_by_id(stored_token.user_id)
        if user is None:
            self._tokens.delete_by_digest(digest)
            raise NotFoundError("Usuario no encontrado")

        if email is not None and email.strip():
            if user.email.lower() != email.strip().lower():
                raise ValidationAppError("Código de recuperación inválido o expirado")

        user.password_hash = hash_password(new_password)
        user.status = "ACTIVA"
        user = self._users.save(user)

        self._tokens.delete_by_digest(digest)
        self._tokens.delete_by_user_and_purpose(user.id, "session")
        return user

    def authenticate_session(self, raw_token: str) -> str:
        clean_token = raw_token.strip()
        if not clean_token:
            raise UnauthorizedError("Falta el token de sesión")

        now = self._clock()
        digest = hash_token(clean_token)
        stored_token = self._tokens.find_by_digest(digest)
        if stored_token is None or stored_token.purpose != "session":
            raise UnauthorizedError("Sesión inválida o expirada")
        if stored_token.is_expired(now):
            self._tokens.delete_by_digest(digest)
            raise UnauthorizedError("Sesión inválida o expirada")
        return stored_token.user_id

    def get_profile(self, user_id: str) -> PlayerProfile:
        profile = self._users.get_profile_stats(user_id)
        if profile is None:
            raise NotFoundError("Perfil de jugador no encontrado")
        return profile

    def get_profile_by_token(self, raw_token: str) -> PlayerProfile:
        user_id = self.authenticate_session(raw_token)
        return self.get_profile(user_id)

    def _new_unique_code(self) -> tuple[str, str]:
        for _ in range(50):
            code = self._code_generator()
            digest = hash_token(code)
            if self._tokens.find_by_digest(digest) is None:
                return code, digest
        raise RuntimeError("No se pudo generar un código único")

    @staticmethod
    def _validate_username(username: str) -> None:
        if not username:
            raise ValidationAppError("El nombre de usuario no puede estar vacío")
        if len(username) < 3 or len(username) > 20:
            raise ValidationAppError("El nombre de usuario debe tener entre 3 y 20 caracteres")
        if not _USERNAME_RE.match(username):
            raise ValidationAppError("El usuario solo puede tener letras, números y guion bajo (_)")

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email:
            raise ValidationAppError("El correo no puede estar vacío")
        if not _EMAIL_RE.match(email):
            raise ValidationAppError("El correo tiene un formato inválido")

    @staticmethod
    def _validate_password(password: str) -> None:
        if not password:
            raise ValidationAppError("La contraseña no puede estar vacía")
        if len(password) < 8:
            raise ValidationAppError("La contraseña debe tener al menos 8 caracteres")
        if len(password) > 64:
            raise ValidationAppError("La contraseña no puede superar 64 caracteres")
        if not (_LETTER_RE.search(password) and _DIGIT_RE.search(password)):
            raise ValidationAppError("La contraseña debe incluir al menos una letra y un número")
