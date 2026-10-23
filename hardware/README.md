# Hardware

Panel físico de 5 botones (arriba, abajo, izquierda, derecha, acción) que controla al jugador. Se conecta a la PC por **cable USB**.

```
Botones → Arduino --USB serial--> Puente (PC) --POST JSON--> Backend
                  Simulador --stdout--> Puente
```

| Carpeta / archivo | Contenido |
|---|---|
| `firmware/arduino/` | Código del Arduino que lee los botones y envía los eventos por puerto serial USB |
| `bridge/` | Puente en la PC: lee el puerto serial del Arduino y reenvía los eventos al backend |
| `simulador/` | Simulador del panel: emite exactamente los mismos mensajes que el Arduino |
| `PROTOCOL.md` | Contrato entre el puente y el backend: mensaje JSON, rutas y vinculación |

El simulador permite desarrollar y probar sin el hardware real. Pasar del simulador al Arduino solo cambia el origen de los mensajes, no su formato. La decisión de usar USB está en [`ADR-008`](../docs/adr/ADR-008-conexion-hardware-usb-serial.md).

---

## Comunicación USB (Arduino ↔ puente)

Este es el tramo físico Arduino → PC por cable USB. El tramo puente → backend (JSON, rutas y vinculación) está en [`PROTOCOL.md`](PROTOCOL.md).

### Parámetros del puerto

| Parámetro | Valor |
|---|---|
| Conexión | Cable USB (el Arduino aparece como puerto serial: `/dev/ttyACM0`, `/dev/ttyUSB0`, `COM3`…) |
| Velocidad | 9600 baudios |
| Formato | 8N1 |
| Codificación | ASCII, una línea por mensaje, terminada en `\n` (se acepta `\r\n`) |

### Mensajes Arduino → PC

| Línea | Cuándo se envía | Significado |
|---|---|---|
| `HELLO <deviceId> <version>` | Al iniciar el Arduino y al recibir `WHO` | Anuncia el panel (base de la vinculación, US-013) |
| `BTN <BOTON> press` | Al presionar un botón | `<BOTON>` ∈ `UP`, `DOWN`, `LEFT`, `RIGHT`, `ACTION` |
| `BTN <BOTON> release` | Al soltar un botón | Igual que arriba |

Ejemplos:

```
HELLO panel-01 1
BTN ACTION press
BTN ACTION release
```

### Mensajes PC → Arduino

| Línea | Efecto |
|---|---|
| `WHO` | El Arduino responde con `HELLO …` (útil si el puente se conecta cuando el Arduino ya estaba encendido) |

### Qué hace el puente con cada línea

1. La valida: una línea desconocida o un botón inválido se descarta y se registra una advertencia.
2. Con `HELLO` guarda el `deviceId`.
3. Con `BTN` arma el mensaje JSON de `PROTOCOL.md` y le agrega `timestamp` (el Arduino no tiene reloj real).
4. Lo envía al backend. Si el backend no responde, el puente sigue leyendo botones y registra el fallo.

### Notas

- El Arduino Uno/Nano se **reinicia** al abrir el puerto serial; por eso envía `HELLO` en cada arranque.
- El anti-rebote (20 ms) se hace en el firmware, así que el puente no filtra eventos.
- El backend corre en Docker y no ve los puertos USB de la PC; por eso el puente corre **fuera** de Docker, en la PC donde está conectado el panel.
- El simulador emite estas mismas líneas, de modo que el puente y el backend no distinguen entre el panel real y el simulado.

---

## Firmware (Arduino)

Sketch: [`firmware/arduino/arduino.ino`](firmware/arduino/arduino.ino).

### Conexión de los botones

Cada botón va entre el pin y **GND**. No hacen falta resistencias externas (se usa `INPUT_PULLUP`).

| Botón | Código | Pin |
|---|---|---|
| Arriba | `UP` | D2 |
| Abajo | `DOWN` | D3 |
| Izquierda | `LEFT` | D4 |
| Derecha | `RIGHT` | D5 |
| Acción | `ACTION` | D6 |

### Cargar el sketch

1. Abrir `arduino.ino` en el Arduino IDE (2.x) o usar `arduino-cli`. El archivo se llama igual que su carpeta porque el IDE lo exige.
2. Elegir la placa y el puerto USB.
3. Cargar. Con el Monitor Serie a **9600 baudios** se ve `HELLO panel-01 1` y, al presionar un botón, `BTN UP press` / `BTN UP release`.

Con `arduino-cli` (ejemplo para Arduino Uno):

```
cd hardware/firmware/arduino
arduino-cli compile --fqbn arduino:avr:uno .
arduino-cli upload  --fqbn arduino:avr:uno -p /dev/ttyACM0 .
```

### Varios paneles

Cambiar la constante `DEVICE_ID` (`panel-01`, `panel-02`, …) antes de cargar cada placa. Debe ser único.

> Cerrar el Monitor Serie antes de ejecutar el puente: solo un programa puede abrir el puerto a la vez.

---

## Puente (USB serial → backend)

Programa de la PC que lee el Arduino y reenvía cada evento de botón al backend. Corre **fuera de Docker** (el contenedor del backend no ve los puertos USB de la PC).

### Instalación

Requiere Python 3.10+.

```
cd hardware/bridge
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Uso

| Caso | Comando |
|---|---|
| Arduino real, detectar el puerto solo | `python -m reactor_bridge` |
| Arduino real, puerto fijo | `python -m reactor_bridge --port /dev/ttyACM0` (Windows: `--port COM3`) |
| Ver el JSON sin backend | `python -m reactor_bridge --sink stdout` |
| Con el simulador | Ver la sección del simulador: se conecta con una tubería `\|` y `--source stdin` |

En Linux, el usuario debe pertenecer al grupo `dialout` para abrir `/dev/ttyACM0` (`sudo usermod -aG dialout $USER` y volver a iniciar sesión).

### Opciones

| Opción | Variable de entorno | Por defecto |
|---|---|---|
| `--port` | `HARDWARE_SERIAL_PORT` | `auto` |
| `--baud` | `HARDWARE_BAUD` | `9600` |
| `--backend-url` | `HARDWARE_BACKEND_URL` | `http://localhost:8000/api/v1/hardware/events` |
| `--device-id` | `HARDWARE_DEVICE_ID` | el que anuncia el Arduino (`HELLO`) |
| `--source` | — | `serial` (`stdin` para el simulador) |
| `--sink` | — | `http` (`stdout` para pruebas) |

> La URL del backend es **provisional**: el endpoint de eventos de hardware aún no existe y su contrato se define en el Sprint 2 (`PROTOCOL.md`). Cuando se defina, solo hay que cambiar el valor por defecto o la variable de entorno.

### Comportamiento

- Si se desconecta el cable USB, el puente reintenta abrir el puerto cada 2 s sin cerrarse.
- El envío al backend va en un hilo aparte con un tiempo máximo de 0,4 s por mensaje, para cuidar la latencia objetivo (< 500 ms, RNF-02). Si el backend falla, el evento se descarta y se registra una advertencia; la lectura de botones continúa.
- Las líneas inválidas del serial se descartan con una advertencia.

### Estructura

| Archivo | Responsabilidad |
|---|---|
| `bridge/reactor_bridge/protocol.py` | Interpreta las líneas del Arduino y arma el mensaje JSON |
| `bridge/reactor_bridge/sources.py` | Origen de líneas: `SerialSource` (USB) y `StdinSource` (simulador) |
| `bridge/reactor_bridge/sinks.py` | Destino: `HttpSink` (backend) y `StdoutSink` (pruebas) |
| `bridge/reactor_bridge/service.py` | Conecta origen → protocolo → destino |
| `bridge/reactor_bridge/__main__.py` | Línea de comandos |

Origen y destino son intercambiables (principio de inversión de dependencias): agregar WebSocket u otro origen es una clase nueva, sin tocar el resto.

### Pruebas

```
cd hardware/bridge
pytest
```

Incluyen una prueba de contrato que verifica que lo que emite el simulador es lo que entiende el puente.

---

## Simulador del panel

Script `simulador/simulador.py`. Emite **exactamente las mismas líneas** que el Arduino por USB (ver [Comunicación USB](#comunicación-usb-arduino--puente)). No necesita dependencias externas (solo Python 3.10+).

### Uso

Desde `hardware/simulador`:

```
# Teclado: escribe teclas y Enter (w=ARRIBA s=ABAJO a=IZQUIERDA d=DERECHA e=ACCION)
python simulador.py --interactive

# Secuencia de ejemplo (agregar --repeat para repetirla sin parar)
python simulador.py --demo
```

Conectado al puente (Linux/macOS, desde `hardware/simulador`):

```
python simulador.py --interactive | PYTHONPATH=../bridge python -m reactor_bridge --source stdin --sink stdout
```

Ejemplo de salida del simulador:

```
HELLO panel-sim-01 1
BTN RIGHT press
BTN RIGHT release
```

### Opciones

| Opción | Descripción |
|---|---|
| `--interactive` / `--demo` | Modo de operación (uno es obligatorio) |
| `--device-id` | Identificador del panel simulado (por defecto `panel-sim-01`) |
| `--hold-ms` | Milisegundos entre `press` y `release` (por defecto 80) |
| `--repeat` | Con `--demo`, repite la secuencia |
| `--output RUTA` | Escribe en un archivo o puerto virtual en lugar de stdout |

Los mensajes de ayuda salen por stderr, así que la salida estándar solo contiene líneas del protocolo.

### Cuando llegue el Arduino real

Solo cambia el origen: `python -m reactor_bridge` (sin `--source stdin`). El formato de los mensajes no cambia.
