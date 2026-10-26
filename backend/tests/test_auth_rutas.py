"""Pruebas de contrato HTTP para las rutas /api/v1/auth/*."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.shared.events import PasswordResetRequested, UserRegistered
from tests.conftest import make_container

BASE = "/api/v1/auth"


@pytest.fixture
def app_and_events():
    container = make_container()
    events = []
    container.event_bus.subscribe(UserRegistered, events.append)
    container.event_bus.subscribe(PasswordResetRequested, events.append)
    client = TestClient(create_app(container))
    return client, events


def test_flujo_completo_registro_verificacion_login_perfil_y_recuperacion(app_and_events):
    client, events = app_and_events

    # 1. Registro (acepta campos en inglés o español)
    reg = client.post(
        f"{BASE}/register",
        json={"username": "Jordanny_1", "email": "jordanny@tec.ac.cr", "password": "Password123"},
    )
    assert reg.status_code == 201
    reg_body = reg.json()
    assert reg_body["username"] == "Jordanny_1"
    assert reg_body["status"] == "PENDIENTE_VERIFICACION"
    assert len(events) == 1 and isinstance(events[0], UserRegistered)
    verify_code = events[0].verification_token

    # 2. Login antes de verificar correo -> 403 FORBIDDEN
    early_login = client.post(
        f"{BASE}/login",
        json={"email": "jordanny@tec.ac.cr", "password": "Password123"},
    )
    assert early_login.status_code == 403
    assert early_login.json()["error"]["code"] == "FORBIDDEN"

    # 3. Verificación de correo
    ver = client.post(
        f"{BASE}/verify-email",
        json={"code": verify_code, "email": "jordanny@tec.ac.cr"},
    )
    assert ver.status_code == 200
    assert ver.json()["status"] == "ACTIVA"

    # 4. Login exitoso
    log = client.post(
        f"{BASE}/login",
        json={"email": "jordanny@tec.ac.cr", "password": "Password123"},
    )
    assert log.status_code == 200
    log_body = log.json()
    token = log_body["token"]
    assert token
    assert log_body["user"]["username"] == "Jordanny_1"

    # 5. Consulta de perfil autenticado
    prof = client.get(f"{BASE}/profile", headers={"Authorization": f"Bearer {token}"})
    assert prof.status_code == 200
    assert prof.json() == {
        "nombre_usuario": "Jordanny_1",
        "partidas_jugadas": 0,
        "partidas_ganadas": 0,
        "puntos_totales": 0,
    }
    assert client.get(f"{BASE}/profile").status_code == 401

    # 6. Solicitud de recuperación de contraseña
    forgot = client.post(f"{BASE}/forgot-password", json={"email": "jordanny@tec.ac.cr"})
    assert forgot.status_code == 200
    assert isinstance(events[-1], PasswordResetRequested)
    reset_code = events[-1].reset_token

    # 7. Restablecer contraseña (revoca la sesión anterior)
    reset = client.post(
        f"{BASE}/reset-password",
        json={"code": reset_code, "new_password": "NuevaPassword99", "email": "jordanny@tec.ac.cr"},
    )
    assert reset.status_code == 200
    assert client.get(f"{BASE}/profile", headers={"Authorization": f"Bearer {token}"}).status_code == 401

    # 8. Login con la contraseña anterior falla (401) y con la nueva funciona (200)
    assert (
        client.post(f"{BASE}/login", json={"email": "jordanny@tec.ac.cr", "password": "Password123"}).status_code
        == 401
    )
    assert (
        client.post(f"{BASE}/login", json={"email": "jordanny@tec.ac.cr", "password": "NuevaPassword99"}).status_code
        == 200
    )


def test_rutas_aceptan_alias_en_espanol(app_and_events):
    client, events = app_and_events

    reg = client.post(
        f"{BASE}/register",
        json={"usuario": "Jugador_ES", "correo": "es@tec.ac.cr", "clave": "Password123"},
    )
    assert reg.status_code == 201
    code = events[-1].verification_token

    ver = client.post(f"{BASE}/verify-email", json={"codigo": code, "correo": "es@tec.ac.cr"})
    assert ver.status_code == 200

    log = client.post(f"{BASE}/login", json={"correo": "es@tec.ac.cr", "clave": "Password123"})
    assert log.status_code == 200
