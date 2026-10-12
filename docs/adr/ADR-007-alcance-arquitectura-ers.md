# ADR-007 — Componentes de la ERS diferidos para después del Sprint 2

**Estado:** Aceptada · **Responsable:** Ulfrán Rodríguez

## Contexto
La arquitectura propuesta en la ERS (sección 7) incluye API Gateway, servidor de tiempo real (WebSocket), broker MQTT,
caché Redis, balanceador de carga, Kubernetes y despliegue en un proveedor cloud. La ERS aclara que la arquitectura es una guía
"sin que ello implique que deba implementarse en su totalidad de forma inmediata". El Sprint 2 solo entrega cuentas,
base de datos, Docker, CI y simulador del panel. Además, la ERS (UC-07) define que la partida la hospeda el dispositivo del anfitrión en red LAN.

## Decisión
En el Sprint 2 se construye únicamente: backend REST de cuentas, PostgreSQL y contenedores con Docker Compose.
Quedan diferidos y marcados como "futuro" en los diagramas:
- Servidor de tiempo real y estado de partida: el motor corre en el anfitrión (Godot), no en este backend.
- Broker MQTT: el protocolo del panel lo define Javier; se decide en el Sprint 3 cuando se conecte con el motor.
- Redis: no hay estado efímero de partidas en este backend todavía.
- Balanceador, Kubernetes y cloud: se abordan en el Sprint 5 (despliegue cloud).

## Alternativas consideradas
- Implementar todo el esqueleto de la ERS desde ahora: consume el tiempo del sprint y agrega contenedores que nadie usa todavía.

## Consecuencias
- (+) El Sprint 2 se enfoca en lo evaluable: MVP de cuentas, Docker, base de datos y CI.
- (+) La arquitectura por capas (ADR-002) permite añadir esos componentes sin reescribir lo existente.
- (−) Los diagramas del Sprint 2 difieren de los de la ERS; esta diferencia queda documentada aquí y en la Wiki.
