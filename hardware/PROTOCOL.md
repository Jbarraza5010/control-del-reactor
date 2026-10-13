# Protocolo panel ↔ backend

La decisión de conectar el panel por USB serial con un puente en la PC está justificada en [`ADR-008`](../docs/adr/ADR-008-conexion-hardware-usb-serial.md).

## Transporte

- Dispositivo: **Arduino**
- Conexión Arduino → PC: _Serial por USB_
- PC → backend: un pequeño **puente** (bridge) en la PC donde está conectado el Arduino lee el puerto serial y reenvía cada evento al backend por HTTP (`POST` con JSON, ver [Rutas del backend](#rutas-del-backend))
- Velocidad serial: **9600 baudios** (8N1), el firmware y el puente deben usar el mismo valor
- Latencia objetivo de extremo a extremo: **< 500 ms** (RNF-02)

## Botones

| Botón | Código |
|---|---|
| Arriba | `UP` |
| Abajo | `DOWN` |
| Izquierda | `LEFT` |
| Derecha | `RIGHT` |
| Acción | `ACTION` |

## Mensaje de evento de botón

```json
{
  "deviceId": "panel-01",
  "button": "ACTION",
  "event": "press",
  "timestamp": 1760000000000
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `deviceId` | string | Identificador único del panel |
| `button` | string | `UP`, `DOWN`, `LEFT`, `RIGHT` o `ACTION` |
| `event` | string | `press` o `release` |
| `timestamp` | number | Milisegundos; lo agrega el puente al recibir el evento (el Arduino no tiene reloj real) |

## Vinculación del panel (US-013)

1. El puente anuncia el panel (`POST /api/v1/hardware/devices/announce`) en cuanto recibe el `HELLO` del Arduino.
2. El backend genera un código de vinculación de 6 dígitos y lo devuelve; el puente lo muestra en su consola (el panel no tiene pantalla).
3. El jugador, con sesión iniciada, ingresa el código en el cliente (`POST /api/v1/hardware/link`).
4. El backend asocia `deviceId` ↔ jugador. Desde ese momento, los eventos del panel se le entregan al cliente de ese jugador por WebSocket.

Reglas:

- El código vale **5 minutos** y se usa **una sola vez**. Si el panel se anuncia de nuevo sin estar vinculado, el código anterior se invalida y se genera uno nuevo.
- Un jugador tiene **un solo panel** vinculado y un panel pertenece a **un solo jugador**.
- Un panel ya vinculado que se vuelve a anunciar (por ejemplo, al reiniciar el Arduino) conserva su vínculo; no se genera código.

## Rutas del backend

Prefijo común: `/api/v1/hardware`. Cuerpos en JSON. Los errores usan el formato uniforme del backend (ADR-006):

```json
{ "error": { "code": "NOT_FOUND", "message": "Código de vinculación inválido o expirado" } }
```

| Método y ruta | Quién la llama | Autenticación | Para qué |
|---|---|---|---|
| `POST /api/v1/hardware/devices/announce` | Puente | Ninguna (Sprint 2) | Anunciar el panel y obtener el código de vinculación |
| `POST /api/v1/hardware/events` | Puente | Ninguna (Sprint 2) | Enviar un evento de botón |
| `POST /api/v1/hardware/link` | Cliente | `Authorization: Bearer <token>` | Vincular el panel con el código |
| `GET /api/v1/hardware/link` | Cliente | `Authorization: Bearer <token>` | Consultar el panel vinculado |
| `DELETE /api/v1/hardware/link` | Cliente | `Authorization: Bearer <token>` | Desvincular el panel |
| `GET /api/v1/hardware/ws` (WebSocket) | Cliente | `Authorization: Bearer <token>` en el handshake | Recibir los botones en tiempo real |

### `POST /api/v1/hardware/devices/announce`

Solicitud:

```json
{ "deviceId": "panel-01", "version": 1 }
```

Respuesta `200` si el panel **no** está vinculado:

```json
{
  "deviceId": "panel-01",
  "linked": false,
  "pairingCode": "482915",
  "expiresAt": "2026-10-13T18:05:00Z"
}
```

Respuesta `200` si el panel **ya** está vinculado:

```json
{ "deviceId": "panel-01", "linked": true, "pairingCode": null, "expiresAt": null }
```

| Error | Código | Cuándo |
|---|---|---|
| 400 | `VALIDATION_ERROR` | `deviceId` con formato inválido o `version` no soportada |

### `POST /api/v1/hardware/events`

Solicitud: el [mensaje de evento de botón](#mensaje-de-evento-de-botón).

Respuesta `202` sin cuerpo.

| Error | Código | Cuándo | Qué hace el puente |
|---|---|---|---|
| 400 | `VALIDATION_ERROR` | Botón, evento o campos inválidos | Registra y descarta |
| 404 | `NOT_FOUND` | El `deviceId` nunca se anunció (p. ej., el backend se reinició) | Vuelve a anunciar el panel |
| 409 | `CONFLICT` | El panel no está vinculado a ningún jugador | Registra y descarta |

El puente **no reintenta** eventos fallidos: un movimiento que llega tarde es peor que uno perdido (RNF-02).

### `POST /api/v1/hardware/link`

Solicitud:

```json
{ "pairingCode": "482915" }
```

Respuesta `200`:

```json
{ "deviceId": "panel-01", "linkedAt": "2026-10-13T18:01:12Z" }
```

| Error | Código | Cuándo |
|---|---|---|
| 400 | `VALIDATION_ERROR` | El código no tiene 6 dígitos |
| 401 | `UNAUTHORIZED` | Falta el token o no es válido |
| 404 | `NOT_FOUND` | El código no existe, ya se usó o expiró |
| 409 | `CONFLICT` | El jugador ya tiene otro panel vinculado |

### `GET /api/v1/hardware/link`

Respuesta `200`: igual que la de `POST /link`. `404 NOT_FOUND` si el jugador no tiene panel vinculado; `401 UNAUTHORIZED` sin token válido.

### `DELETE /api/v1/hardware/link`

Respuesta `204` sin cuerpo. `404 NOT_FOUND` si el jugador no tiene panel vinculado; `401 UNAUTHORIZED` sin token válido. Después de desvincular, el panel debe anunciarse de nuevo para obtener un código.

### WebSocket `GET /api/v1/hardware/ws`

El cliente abre la conexión con el token en el handshake (en Godot 4: `WebSocketPeer.handshake_headers`). Si el token no es válido, el servidor cierra con el código `4401`. El servidor solo envía mensajes; el cliente no necesita enviar nada.

Mensajes del servidor al cliente:

| `type` | Cuándo | Campos adicionales |
|---|---|---|
| `button` | El panel del jugador envió un evento | `deviceId`, `button`, `event`, `timestamp` |
| `device.linked` | Se vinculó un panel a este jugador | `deviceId` |
| `device.unlinked` | Se desvinculó el panel de este jugador | `deviceId` |

Ejemplo:

```json
{ "type": "button", "deviceId": "panel-01", "button": "UP", "event": "press", "timestamp": 1760000000000 }
```

## Eventos internos del backend (EventBus)

Dentro del backend, las rutas publican eventos en el `EventBus` (patrón Observer, `app/shared/events.py`) y el WebSocket se suscribe a ellos, así las rutas no conocen a los clientes conectados.

| Evento | Lo publica | Lo consume |
|---|---|---|
| `PanelAnnounced(device_id, pairing_code)` | `announce` | Registro / logs |
| `PanelLinked(device_id, player_id)` | `link` | WebSocket → `device.linked` |
| `PanelUnlinked(device_id, player_id)` | `DELETE /link` | WebSocket → `device.unlinked` |
| `HardwareButtonEvent(device_id, player_id, button, event, timestamp)` | `events` | WebSocket → `button` (y, en el Sprint 3, el motor de juego) |

## Pendientes

- **Autenticación del puente:** en el Sprint 2, `announce` y `events` no piden credenciales, así que cualquiera en la red podría enviar eventos con un `deviceId` ajeno. Se acepta porque el entorno es local; para el despliegue en la nube (Sprint 5) hay que agregar un token por panel.
- **Puente:** hoy solo llama a `events`. Falta que llame a `announce` al recibir el `HELLO`, muestre el código en consola y vuelva a anunciar ante un `404`.
- **Backend:** las rutas de esta sección aún no existen.
