# Hardware

Panel físico de 5 botones (arriba, abajo, izquierda, derecha, acción) que controla al jugador.

| Carpeta / archivo | Contenido |
|---|---|
| `firmware/arduino/` | Código del Arduino que lee los botones y envía los eventos por puerto serial |
| `bridge/` | Puente en la PC: lee el puerto serial del Arduino y reenvía los eventos al backend |
| `simulator/` | Simulador del panel: emite **exactamente** los mismos mensajes que el Arduino |
| `PROTOCOL.md` | Contrato de mensajes entre el panel y el backend |

El simulador permite desarrollar y probar sin el hardware real. Pasar del simulador al Arduino solo cambia el origen de los mensajes, no su formato.
