from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import make_container


def client(db_up: bool = True) -> TestClient:
    return TestClient(create_app(make_container(db_up)))


def test_health_responde_ok():
    res = client().get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_health_db_200_si_la_bd_responde():
    res = client(db_up=True).get("/health/db")
    assert res.status_code == 200
    assert res.json()["database"] == "up"


def test_health_db_503_si_la_bd_no_responde():
    res = client(db_up=False).get("/health/db")
    assert res.status_code == 503
    assert res.json()["database"] == "down"


def test_endpoints_de_auth_pendientes_responden_501():
    res = client().post("/api/v1/auth/login")
    assert res.status_code == 501
    assert res.json()["error"]["code"] == "NOT_IMPLEMENTED"


def test_ruta_inexistente_responde_404_con_formato_de_error():
    res = client().get("/nada")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_documentacion_openapi_disponible():
    assert client().get("/docs").status_code == 200
