# ADR-008: Conexión del panel físico por USB serial con un puente en la PC

- **Estado:** Propuesto
- **Fecha:** 2026-10-12
- **Autor(es):** Jbarraza5010 (rama `feature/hardware`)

## Contexto

El juego se controla con un panel físico de 5 botones (arriba, abajo, izquierda, derecha, acción) basado en Arduino. 

Requisitos que aplican: 
- latencia de movimiento extremo a extremo < 500 ms (RNF-02)
- vinculación del panel con la sesión del jugador (US-013) 
- posibilidad de probar sin el hardware real. 

Además, el backend corre dentro de Docker, desde donde no se puede leer el puerto serial de la PC.

## Opciones consideradas

1. **USB serial + puente en la PC (elegida).** El Arduino envía líneas de texto por USB; un programa en la PC las lee y las reenvía al backend por HTTP. Ventajas: sin módulos extra, sin emparejamiento, latencia baja y estable, fácil de depurar con el Monitor Serie. Desventajas: el panel debe estar conectado por cable a la PC del jugador y hay que ejecutar el puente.
2. **Bluetooth (HC-05).** Inalámbrico, pero exige un módulo adicional, emparejamiento y configuración por sistema operativo, y es más difícil de depurar. Descartada por la decisión del equipo de usar USB.
3. **Pasar el puerto USB al contenedor del backend.** Evitaría el puente, pero depende del sistema operativo (en Windows con Docker Desktop no es directo) y acopla el backend al hardware. Descartada.
4. **Arduino con Wi-Fi (ESP32) hablando directo con el backend.** Elimina el puente, pero requiere otra placa, red y credenciales, y se aleja del hardware disponible. Descartada.

## Decisión

Se usa USB serial a **9600 baudios** con líneas de texto ASCII (`HELLO <deviceId> <version>`, `BTN <BOTON> press|release`; detalle en la sección "Comunicación USB" de `hardware/README.md`) y un puente (`hardware/bridge`) que corre en la PC, valida cada línea, agrega el `timestamp` y envía el mensaje JSON de `PROTOCOL.md` al backend. Un simulador (`hardware/simulador`) emite las mismas líneas para tener la posibilidad de realizar pruebas sin el uso del hardware.

El puente separa origen y destino detrás de interfaces (`LineSource`, `EventSink`), en línea con el patrón Adapter de `backend/.../infrastructure/hardware` y con el principio de inversión de dependencias.

## Consecuencias

- (+) Un solo formato de mensajes para el panel real y el simulador; el backend no distingue entre ambos.
- (+) 9600 baudios es suficiente para el tráfico de un panel de 5 botones y es la velocidad estándar más compatible con placas y adaptadores USB-serial, incluidos los clones.
- (+) Latencia esperada de unos 18 ms por mensaje en el tramo USB (unos 90 ms en el peor caso, con los 5 botones a la vez), dentro del presupuesto de 500 ms (RNF-02).
- (+) El backend no depende de hardware ni del sistema operativo.
- (−) 9600 baudios es 12 veces más lento que 115200. Si en el futuro el panel envía mucho más tráfico (sensores continuos, varios paneles por un mismo cable), habrá que subir la velocidad en `arduino.ino` (`BAUD_RATE`) y en el puente (`--baud` o `HARDWARE_BAUD`) al mismo tiempo; si los dos lados no coinciden, el puente descarta todas las líneas.
- (−) Hay un proceso más que ejecutar en la PC del jugador (el puente).
- (−) El panel queda limitado por la longitud del cable.
- Pendiente: implementar en el backend las rutas y la vinculación definidas en `hardware/PROTOCOL.md`, y que el puente llame a `announce` al recibir el `HELLO`.
