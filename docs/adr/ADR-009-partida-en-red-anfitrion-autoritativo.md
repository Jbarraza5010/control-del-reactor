# ADR-009: Partida en red con anfitrión autoritativo en LAN

- **Estado:** Aceptado
- **Fecha:** 2026-11-16
- **Autor(es):** Ulfrán Rodríguez Cordero (Arquitecto de Software)
- **Relacionado con:** ADR-002 (capas), ADR-008 (panel físico), ADR-010 (patrones del motor), RNF-01, RNF-02

## Contexto

El Sprint 3 pide una partida completa con 2 a 4 jugadores reales, cada uno con su panel físico. Hay que decidir **quién calcula el estado de la partida** (posiciones, puntos, guardianes, eventos, ganador) y **cómo se comunican los clientes**.

Requisitos que aplican:

- RNF-01: al menos 2 jugadores simultáneos (el enunciado del Sprint 3 pide hasta 4 en la división de tareas).
- RNF-02: el movimiento debe verse reflejado en menos de 500 ms.
- La demo es presencial, con todos los equipos en la misma red local.
- Quedan pocos días de Sprint: no se puede mantener el motor del juego en dos lenguajes.
- El cliente es Godot (GDScript) y Godot ya trae multijugador de alto nivel (`ENetMultiplayerPeer`, RPC).

## Opciones consideradas

1. **Anfitrión autoritativo en LAN (elegida).** Un jugador crea la partida y su instancia de Godot ejecuta la `Partida` (ver ADR-010). Los demás clientes envían solo sus entradas y reciben el estado. Ventajas: un solo motor, latencia de LAN (pocos ms), usa lo que Godot ya trae. Desventajas: el anfitrión es punto único de falla y podría hacer trampa; solo funciona en la misma red.
2. **Servidor dedicado en el backend (Python + WebSocket).** Es lo más correcto para jugar por internet y evita trampas, pero obliga a reescribir el motor en Python (o mantenerlo duplicado) y a exponer tiempo real desde Docker. Se descarta para el Sprint 3; queda como evolución para el despliegue en la nube (Sprint 5, ADR-007).
3. **Cada cliente simula y se sincronizan entre sí (peer-to-peer).** Aparecen desincronizaciones y discusiones sobre quién llegó primero al reactor. Se descarta.
4. **Cliente autoritativo (cada quien manda su posición y sus puntos).** Cualquier cliente podría sumarse puntos y no hay árbitro para la disputa del reactor. Se descarta.

## Decisión

Se usa **anfitrión autoritativo** sobre ENet (UDP), puerto por defecto **7777**, con el anfitrión como peer 1 y hasta 3 clientes (4 jugadores en total).

| Quién | Qué hace |
|---|---|
| **Cliente** | Lee su control (teclado o panel físico a través de `PanelHardware`) y envía al anfitrión su **entrada**: dirección y estado del botón ACCIÓN. No calcula puntos ni colisiones con guardianes. |
| **Anfitrión** | Es el único que llama a `Partida.actualizar(delta)`. Mueve a todos los jugadores, ejecuta obstáculos, guardianes y eventos, valida cada acción (`Partida.registrar_puntos`) y decide el ganador. |
| **Anfitrión → clientes** | Instantáneas de posiciones a ~20 Hz (RPC no confiable y ordenado). Mensajes que no se pueden perder (puntaje, cambio de estado de un jugador, evento iniciado o terminado, tiempo, fin de partida) por RPC confiable. |
| **Anfitrión → backend** | Al terminar, envía el `ResultadoPartida` por HTTP para guardar puntos y posiciones en una sola transacción (tarea de Moisés y Javier). |

Tabla de mensajes de red (nombres propuestos, los define Javier al implementar la red):

| Mensaje | Dirección | Canal | Contenido |
|---|---|---|---|
| `entrada` | cliente → anfitrión | no confiable ordenado | `direccion: Vector2`, `accion: bool` |
| `instantanea` | anfitrión → clientes | no confiable ordenado | posiciones de jugadores, guardianes y barreras |
| `puntaje` | anfitrión → clientes | confiable | `jugador_id`, `total`, `delta`, `fuente` |
| `estado_jugador` | anfitrión → clientes | confiable | `jugador_id`, `estado` |
| `evento` | anfitrión → clientes | confiable | `tipo`, `duracion`, iniciado/terminado |
| `fin_partida` | anfitrión → clientes | confiable | `ResultadoPartida` completo |

El contrato del resultado está en `docs/arquitectura/04-motor-de-partida.md`.

## Consecuencias

- (+) Las reglas del juego viven en un solo lugar (`client/scripts/juego/`) y se prueban sin red ni escenas.
- (+) La latencia de una LAN está muy por debajo del límite de 500 ms (RNF-02).
- (+) Los clientes (incluido el móvil Android) son delgados: solo entrada y dibujo.
- (−) Si el anfitrión se cierra, la partida termina y no se guarda resultado. Los clientes deben volver al menú con un mensaje.
- (−) El anfitrión podría alterar el resultado; es aceptable para una demo en LAN y se documenta como riesgo.
- (−) Solo funciona en la misma red. El firewall de Windows debe permitir UDP 7777 en la PC del anfitrión.
- (−) El panel físico de cada jugador habla con el backend (ADR-008), así que todos los puentes y clientes deben apuntar al **mismo backend** (el de la PC del anfitrión). Javier debe confirmarlo al integrar la red.
- Pendiente: definir con Javier cómo se obtiene el "código de partida" (por ejemplo, derivado de la IP del anfitrión) y qué pasa si un cliente se reconecta a mitad de partida.
