from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import create_app
from app.shared.errors import ConflictError
from tests.conftest import make_container


class Body(BaseModel):
    email: str
    edad: int


def app_con_rutas_de_prueba():
    app = create_app(make_container())

    @app.get("/conflicto")
    def conflicto():
        raise ConflictError("correo duplicado")

    @app.get("/boom")
    def boom():
        raise RuntimeError("secreto interno")

    @app.post("/con-cuerpo")
    def con_cuerpo(body: Body):
        return body

    return app


def test_apperror_se_traduce_a_su_codigo_http_y_formato_uniforme():
    res = TestClient(app_con_rutas_de_prueba()).get("/conflicto")
    assert res.status_code == 409
    assert res.json()["error"] == {"code": "CONFLICT", "message": "correo duplicado"}


def test_validacion_de_entrada_devuelve_400_validation_error():
    res = TestClient(app_con_rutas_de_prueba()).post("/con-cuerpo", json={"email": "a@b.com", "edad": "x"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_json_malformado_devuelve_400():
    res = TestClient(app_con_rutas_de_prueba()).post(
        "/con-cuerpo", content="{mal", headers={"Content-Type": "application/json"}
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_error_inesperado_devuelve_500_sin_filtrar_detalles():
    res = TestClient(app_con_rutas_de_prueba(), raise_server_exceptions=False).get("/boom")
    assert res.status_code == 500
    assert "secreto interno" not in res.text
    assert res.json()["error"]["code"] == "INTERNAL_ERROR"
