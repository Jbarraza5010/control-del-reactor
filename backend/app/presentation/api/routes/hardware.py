"""Rutas del panel físico (US-013). Contrato completo en hardware/PROTOCOL.md.

- El puente llama a  POST /devices/announce  y  POST /events  (sin credenciales en el Sprint 2).
- El cliente llama a  /link  y abre el WebSocket  /ws  con  Authorization: Bearer <token>.
"""
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, Response, WebSocket
from pydantic import BaseModel, ConfigDict, Field

from app.application.ports.player_identity import PlayerIdentity
from app.container import Container
from app.domain.entities.hardware_panel import DEVICE_ID_PATTERN, HardwarePanel
from app.presentation.api.dependencies import get_container
from app.shared.errors import UnauthorizedError

router = APIRouter(prefix="/api/v1/hardware", tags=["hardware"])


# ---- Esquemas (JSON en camelCase, como en PROTOCOL.md) ------------------------
class _CamelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class AnnounceRequest(_CamelModel):
    device_id: str = Field(alias="deviceId", pattern=DEVICE_ID_PATTERN, examples=["panel-01"])
    version: int = Field(examples=[1])


class AnnounceResponse(_CamelModel):
    device_id: str = Field(serialization_alias="deviceId")
    linked: bool
    pairing_code: str | None = Field(serialization_alias="pairingCode")
    expires_at: str | None = Field(serialization_alias="expiresAt")


class ButtonEventRequest(_CamelModel):
    device_id: str = Field(alias="deviceId", pattern=DEVICE_ID_PATTERN, examples=["panel-01"])
    button: Literal["UP", "DOWN", "LEFT", "RIGHT", "ACTION"]
    event: Literal["press", "release"]
    timestamp: int = Field(ge=0, examples=[1760000000000])


class LinkRequest(_CamelModel):
    pairing_code: str = Field(alias="pairingCode", examples=["482915"])


class LinkResponse(_CamelModel):
    device_id: str = Field(serialization_alias="deviceId")
    linked_at: str = Field(serialization_alias="linkedAt")


def _iso(moment: datetime | None) -> str | None:
    if moment is None:
        return None
    return moment.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _link_response(panel: HardwarePanel) -> LinkResponse:
    return LinkResponse(device_id=panel.device_id, linked_at=_iso(panel.linked_at))


# ---- Autenticación del jugador -------------------------------------------------
def player_from_authorization(value: str | None, identity: PlayerIdentity) -> str:
    if not value:
        raise UnauthorizedError("Falta el token de sesión")
    scheme, _, token = value.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise UnauthorizedError("Usa el encabezado 'Authorization: Bearer <token>'")
    return identity.player_id_from_token(token.strip())


def current_player(
    authorization: Annotated[str | None, Header()] = None,
    container: Container = Depends(get_container),
) -> str:
    return player_from_authorization(authorization, container.player_identity)


# ---- Rutas del puente ------------------------------------------------------------
@router.post(
    "/devices/announce",
    response_model=AnnounceResponse,
    response_model_by_alias=True,
    summary="El puente anuncia el panel y obtiene el código de vinculación",
)
def announce(body: AnnounceRequest, container: Container = Depends(get_container)) -> AnnounceResponse:
    panel = container.hardware_service.announce(body.device_id, body.version)
    return AnnounceResponse(
        device_id=panel.device_id,
        linked=panel.is_linked,
        pairing_code=panel.pairing_code,
        expires_at=_iso(panel.pairing_expires_at),
    )


@router.post("/events", status_code=202, summary="El puente envía un evento de botón")
def button_event(body: ButtonEventRequest, container: Container = Depends(get_container)) -> Response:
    container.hardware_service.handle_button(body.device_id, body.button, body.event, body.timestamp)
    return Response(status_code=202)


# ---- Rutas del cliente -----------------------------------------------------------
@router.post("/link", response_model=LinkResponse, response_model_by_alias=True, summary="Vincular el panel con el código")
def link(
    body: LinkRequest,
    player_id: str = Depends(current_player),
    container: Container = Depends(get_container),
) -> LinkResponse:
    return _link_response(container.hardware_service.link(player_id, body.pairing_code))


@router.get("/link", response_model=LinkResponse, response_model_by_alias=True, summary="Consultar el panel vinculado")
def get_link(player_id: str = Depends(current_player), container: Container = Depends(get_container)) -> LinkResponse:
    return _link_response(container.hardware_service.get_link(player_id))


@router.delete("/link", status_code=204, summary="Desvincular el panel")
def unlink(player_id: str = Depends(current_player), container: Container = Depends(get_container)) -> Response:
    container.hardware_service.unlink(player_id)
    return Response(status_code=204)


@router.websocket("/ws")
async def hardware_ws(websocket: WebSocket) -> None:
    """Envía al cliente los botones de SU panel. Token en el handshake; si no es válido, cierra con 4401.

    Además del encabezado Authorization se acepta ?token=<token> para probar con herramientas
    que no permiten encabezados (por ejemplo, desde el navegador).
    """
    container: Container = websocket.app.state.container
    await websocket.accept()
    header = websocket.headers.get("authorization")
    query_token = websocket.query_params.get("token")
    try:
        if header is None and query_token:
            header = f"Bearer {query_token}"
        player_id = player_from_authorization(header, container.player_identity)
    except UnauthorizedError as exc:
        await websocket.close(code=4401, reason=exc.message)
        return
    await websocket.app.state.hardware_hub.serve(websocket, player_id)
