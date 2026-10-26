"""Pruebas unitarias y de integración SQL de AuthService (US-001 a US-007)."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.application.services.auth_service import AuthService, hash_token
from app.infrastructure.auth.dev_player_identity import DevPlayerIdentity
from app.infrastructure.persistence.memory.in_memory_auth_token_repository import (
    InMemoryAuthTokenRepository,
)
from app.infrastructure.persistence.memory.in_memory_user_repository import InMemoryUserRepository
from app.infrastructure.persistence.sql.models import PerfilJugadorModel
from app.shared.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationAppError,
)
from app.shared.events import EventBus, PasswordResetRequested, UserRegistered

T0 = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self) -> None:
        self.now = T0

    def __call__(self) -> datetime:
        return self.now


def make_service(users=None, tokens=None, codes=("123456", "654321", "999999")):
    bus = EventBus()
    clock = Clock()
    events = []
    bus.subscribe(UserRegistered, events.append)
    bus.subscribe(PasswordResetRequested, events.append)
    code_iter = iter(codes)
    user_repo = users or InMemoryUserRepository()
    token_repo = tokens or InMemoryAuthTokenRepository()
    service = AuthService(
        user_repository=user_repo,
        token_repository=token_repo,
        event_bus=bus,
        clock=clock,
        code_generator=lambda: next(code_iter),
    )
    return service, user_repo, token_repo, clock, events


def test_registro_crea_usuario_pendiente_y_publica_evento_con_codigo():
    service, _, _, _, events = make_service()
    user = service.register("Reactor_1", "Jugador@TEC.ac.cr", "Clave1234")
    assert user.username == "Reactor_1"
    assert user.email == "jugador@tec.ac.cr"
    assert user.status == "PENDIENTE_VERIFICACION"
    assert user.password_hash.startswith("pbkdf2_sha256$")
    assert events == [UserRegistered(user_id=user.id, email="jugador@tec.ac.cr", verification_token="123456")]


def test_registro_sql_crea_perfil_jugador_junto_con_usuario(sql_repository, sql_token_repository, sql_session_factory):
    service, _, _, _, _ = make_service(users=sql_repository, tokens=sql_token_repository)
    user = service.register("Moises_1", "moises@tec.ac.cr", "Clave1234")
    with sql_session_factory() as session:
        perfil = session.get(PerfilJugadorModel, user.id)
        assert perfil is not None
        assert perfil.nivel == 1


def test_registro_rechaza_usuario_o_correo_duplicado():
    service, _, _, _, _ = make_service()
    service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    with pytest.raises(ConflictError):
        service.register("reactor_1", "otro@tec.ac.cr", "Clave1234")
    with pytest.raises(ConflictError):
        service.register("Otro_User", "JUGADOR@tec.ac.cr", "Clave1234")


@pytest.mark.parametrize(
    "username,email,password",
    [
        ("ab", "valido@tec.ac.cr", "Clave1234"),
        ("usuario_demasiado_largo_123", "valido@tec.ac.cr", "Clave1234"),
        ("con espacio", "valido@tec.ac.cr", "Clave1234"),
        ("Valido_1", "correo-invalido", "Clave1234"),
        ("Valido_1", "valido@tec.ac.cr", "corta1"),
        ("Valido_1", "valido@tec.ac.cr", "sololetras"),
        ("Valido_1", "valido@tec.ac.cr", "12345678"),
    ],
)
def test_registro_valida_formato_de_campos(username, email, password):
    service, _, _, _, _ = make_service()
    with pytest.raises(ValidationAppError):
        service.register(username, email, password)


def test_verificacion_activa_la_cuenta_y_consume_el_codigo_una_sola_vez():
    service, _, _, _, _ = make_service()
    service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    verified = service.verify_email("123456", "jugador@tec.ac.cr")
    assert verified.status == "ACTIVA"
    with pytest.raises(ValidationAppError):
        service.verify_email("123456")


def test_verificacion_rechaza_codigo_expirado():
    service, _, _, clock, _ = make_service()
    service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    clock.now = T0 + timedelta(hours=24, seconds=1)
    with pytest.raises(ValidationAppError):
        service.verify_email("123456")


def test_login_requiere_cuenta_verificada_y_emite_token_de_sesion():
    service, _, token_repo, clock, _ = make_service()
    user = service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    with pytest.raises(ForbiddenError):
        service.login("jugador@tec.ac.cr", "Clave1234")

    service.verify_email("123456")
    result = service.login("JUGADOR@tec.ac.cr", "Clave1234")
    assert result.user.id == user.id
    assert len(result.token) > 20

    identity = DevPlayerIdentity(token_repo, clock=clock)
    assert identity.player_id_from_token(result.token) == user.id


def test_login_rechaza_credenciales_invalidas():
    service, _, _, _, _ = make_service()
    service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    service.verify_email("123456")
    with pytest.raises(UnauthorizedError):
        service.login("jugador@tec.ac.cr", "OtraClave1")
    with pytest.raises(UnauthorizedError):
        service.login("nadie@tec.ac.cr", "Clave1234")


def test_recuperacion_actualiza_clave_consume_codigo_y_revoca_sesiones():
    service, _, token_repo, _, events = make_service()
    user = service.register("Reactor_1", "jugador@tec.ac.cr", "Clave1234")
    service.verify_email("123456")
    sesion = service.login("jugador@tec.ac.cr", "Clave1234")
    assert token_repo.find_by_digest(hash_token(sesion.token)) is not None

    service.forgot_password("jugador@tec.ac.cr")
    assert isinstance(events[-1], PasswordResetRequested)
    assert events[-1].reset_token == "654321"

    service.reset_password("654321", "NuevaClave99", "jugador@tec.ac.cr")
    assert token_repo.find_by_digest(hash_token(sesion.token)) is None

    with pytest.raises(ValidationAppError):
        service.reset_password("654321", "OtraClave88")
    with pytest.raises(UnauthorizedError):
        service.login("jugador@tec.ac.cr", "Clave1234")
    nuevo_login = service.login("jugador@tec.ac.cr", "NuevaClave99")
    assert nuevo_login.user.id == user.id


def test_forgot_password_de_correo_inexistente_es_404():
    service, _, _, _, _ = make_service()
    with pytest.raises(NotFoundError):
        service.forgot_password("noexiste@tec.ac.cr")

