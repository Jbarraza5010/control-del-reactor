# Protocolo panel ↔ backend (borrador)

> Borrador para completar en el Sprint 2. El protocolo definitivo se justifica en un ADR.

## Transporte

- Dispositivo: **Arduino**
- Conexión Arduino → PC: _Serial por USB (o Bluetooth con módulo HC-05) — por definir_
- PC → backend: un pequeño **puente** (bridge) en la PC donde está conectado el Arduino lee el puerto serial y reenvía cada evento al backend por WebSocket/HTTP
- Velocidad serial: _por definir (p. ej. 9600 o 115200 baudios)_
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

1. El panel se anuncia con su `deviceId`.
2. El backend genera un código de vinculación.
3. El jugador ingresa el código en el cliente.
4. El backend asocia `deviceId` ↔ sesión del jugador.

_Tópicos/rutas y mensajes de vinculación: por definir._
