"""Rutas HTTP y WebSocket del panel físico (contrato de hardware/PROTOCOL.md)."""
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import create_app
from tests.conftest import make_container

BASE = "/api/v1/hardware"


def auth(player="jugador-1"):
    return {"Authorization": f"Bearer {player}"}


def button(button="UP", event="press", device="panel-01", ts=1760000000000):
    return {"deviceId": device, "button": button, "event": event, "timestamp": ts}


@pytest.fixture
def client():
    return TestClient(create_app(make_container()))


def announce_and_link(client, device="panel-01", player="jugador-1"):
    code = client.post(f"{BASE}/devices/announce", json={"deviceId": device, "version": 1}).json()["pairingCode"]
    res = client.post(f"{BASE}/link", json={"pairingCode": code}, headers=auth(player))
    assert res.status_code == 200, res.text
    return code


def test_announce_devuelve_codigo_y_vencimiento(client):
    res = client.post(f"{BASE}/devices/announce", json={"deviceId": "panel-01", "version": 1})
    assert res.status_code == 200
    body = res.json()
    assert body["deviceId"] == "panel-01" and body["linked"] is False
    assert len(body["pairingCode"]) == 6 and body["pairingCode"].isdigit()
    assert body["expiresAt"].endswith("Z")


def test_announce_de_panel_vinculado(client):
    announce_and_link(client)
    body = client.post(f"{BASE}/devices/announce", json={"deviceId": "panel-01", "version": 1}).json()
    assert body == {"deviceId": "panel-01", "linked": True, "pairingCode": None, "expiresAt": None}


@pytest.mark.parametrize(
    "payload", [{"deviceId": "panel 01", "version": 1}, {"deviceId": "panel-01", "version": 2}, {"deviceId": "panel-01"}]
)
def test_announce_invalido_es_400(client, payload):
    res = client.post(f"{BASE}/devices/announce", json=payload)
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_events_responde_202_sin_cuerpo(client):
    announce_and_link(client)
    res = client.post(f"{BASE}/events", json=button())
    assert res.status_code == 202 and res.content == b""


@pytest.mark.parametrize(
    "payload",
    [button(button="JUMP"), button(event="hold"), {"deviceId": "panel-01", "button": "UP", "event": "press"}],
)
def test_events_invalido_es_400(client, payload):
    assert client.post(f"{BASE}/events", json=payload).status_code == 400


def test_events_de_panel_no_anunciado_es_404(client):
    res = client.post(f"{BASE}/events", json=button())
    assert res.status_code == 404 and res.json()["error"]["code"] == "NOT_FOUND"


def test_events_de_panel_sin_vincular_es_409(client):
    client.post(f"{BASE}/devices/announce", json={"deviceId": "panel-01", "version": 1})
    res = client.post(f"{BASE}/events", json=button())
    assert res.status_code == 409 and res.json()["error"]["code"] == "CONFLICT"


def test_link_get_y_delete(client):
    announce_and_link(client)
    got = client.get(f"{BASE}/link", headers=auth())
    assert got.status_code == 200 and got.json()["deviceId"] == "panel-01"
    assert got.json()["linkedAt"].endswith("Z")
    assert client.delete(f"{BASE}/link", headers=auth()).status_code == 204
    assert client.get(f"{BASE}/link", headers=auth()).status_code == 404
    assert client.delete(f"{BASE}/link", headers=auth()).status_code == 404


def test_link_con_codigo_inexistente_404_y_formato_invalido_400(client):
    assert client.post(f"{BASE}/link", json={"pairingCode": "000000"}, headers=auth()).status_code == 404
    assert client.post(f"{BASE}/link", json={"pairingCode": "12"}, headers=auth()).status_code == 400


def test_link_jugador_con_otro_panel_409(client):
    announce_and_link(client, device="panel-01")
    code = client.post(f"{BASE}/devices/announce", json={"deviceId": "panel-02", "version": 1}).json()["pairingCode"]
    assert client.post(f"{BASE}/link", json={"pairingCode": code}, headers=auth()).status_code == 409


@pytest.mark.parametrize("headers", [{}, {"Authorization": "jugador-1"}, {"Authorization": "Bearer "}, {"Authorization": "Bearer a b"}])
def test_rutas_del_cliente_sin_token_valido_401(client, headers):
    for method in ("get", "delete"):
        res = getattr(client, method)(f"{BASE}/link", headers=headers)
        assert res.status_code == 401 and res.json()["error"]["code"] == "UNAUTHORIZED"
    assert client.post(f"{BASE}/link", json={"pairingCode": "123456"}, headers=headers).status_code == 401


def test_websocket_entrega_los_botones_solo_al_dueno_del_panel(client):
    announce_and_link(client, device="panel-01", player="jugador-1")
    announce_and_link(client, device="panel-02", player="jugador-2")
    with client.websocket_connect(f"{BASE}/ws", headers=auth("jugador-1")) as ws1, client.websocket_connect(
        f"{BASE}/ws", headers=auth("jugador-2")
    ) as ws2:
        client.post(f"{BASE}/events", json=button("LEFT", device="panel-01"))
        client.post(f"{BASE}/events", json=button("ACTION", "release", device="panel-02"))
        assert ws1.receive_json() == {
            "type": "button", "deviceId": "panel-01", "button": "LEFT", "event": "press", "timestamp": 1760000000000
        }
        assert ws2.receive_json()["button"] == "ACTION"


def test_websocket_avisa_vinculacion_y_desvinculacion(client):
    with client.websocket_connect(f"{BASE}/ws", headers=auth()) as ws:
        announce_and_link(client)
        assert ws.receive_json() == {"type": "device.linked", "deviceId": "panel-01"}
        client.delete(f"{BASE}/link", headers=auth())
        assert ws.receive_json() == {"type": "device.unlinked", "deviceId": "panel-01"}


def test_websocket_acepta_token_por_query_string(client):
    announce_and_link(client)
    with client.websocket_connect(f"{BASE}/ws?token=jugador-1") as ws:
        client.post(f"{BASE}/events", json=button("DOWN"))
        assert ws.receive_json()["button"] == "DOWN"


def test_websocket_sin_token_cierra_con_4401(client):
    with client.websocket_connect(f"{BASE}/ws") as ws:
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
    assert exc.value.code == 4401


def test_websocket_libera_la_suscripcion_al_cerrarse(client):
    hub = client.app.state.hardware_hub
    with client.websocket_connect(f"{BASE}/ws", headers=auth()):
        pass
    # La conexión se cierra en segundo plano; espera breve hasta que el hub la libere.
    import time

    for _ in range(50):
        if hub.connection_count("jugador-1") == 0:
            break
        time.sleep(0.02)
    assert hub.connection_count("jugador-1") == 0


def test_rutas_de_hardware_aparecen_en_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]
    for path in ("/devices/announce", "/events", "/link"):
        assert f"{BASE}{path}" in paths
