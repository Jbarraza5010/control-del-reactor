/*
 * Control del Reactor - Firmware del panel de 5 botones.
 * (El archivo se llama arduino.ino porque el Arduino IDE exige que coincida con el nombre de su carpeta.)
 *
 * Lee los botones (ARRIBA, ABAJO, IZQUIERDA, DERECHA, ACCION) y envia cada
 * cambio al PC por el puerto serial USB, una linea de texto por evento.
 * Formato completo en hardware/README.md (seccion "Comunicacion USB").
 *
 *   Arduino -> PC:  HELLO <deviceId> <version>   (al iniciar y al recibir "WHO")
 *                   BTN <BOTON> press|release
 *   PC -> Arduino:  WHO                          (pide repetir el HELLO)
 *
 * Conexion: cada boton entre su pin y GND (se usa la resistencia pull-up interna).
 */

#include <Arduino.h>

// ---- Configuracion -------------------------------------------------------
static const char DEVICE_ID[] = "panel-01";   // Debe ser unico por panel
static const uint8_t PROTOCOL_VERSION = 1;
static const unsigned long BAUD_RATE = 9600;
static const unsigned long DEBOUNCE_MS = 20;  // Tiempo que la lectura debe ser estable

struct Button {
  const char *name;        // Codigo del protocolo (PROTOCOL.md)
  uint8_t pin;
  bool pressed;            // Estado ya notificado al PC
  bool lastReading;        // Ultima lectura cruda
  unsigned long lastChange;
};

static Button buttons[] = {
  {"UP",     2, false, false, 0},
  {"DOWN",   3, false, false, 0},
  {"LEFT",   4, false, false, 0},
  {"RIGHT",  5, false, false, 0},
  {"ACTION", 6, false, false, 0},
};
static const uint8_t BUTTON_COUNT = sizeof(buttons) / sizeof(buttons[0]);

// ---- Entrada serial (comando WHO) ----------------------------------------
static char inputBuffer[16];
static uint8_t inputLength = 0;

static void sendHello() {
  Serial.print(F("HELLO "));
  Serial.print(DEVICE_ID);
  Serial.print(' ');
  Serial.println(PROTOCOL_VERSION);
}

static void sendButtonEvent(const Button &button, bool pressed) {
  Serial.print(F("BTN "));
  Serial.print(button.name);
  Serial.println(pressed ? F(" press") : F(" release"));
}

static void handleCommand(const char *command) {
  if (strcmp(command, "WHO") == 0) {
    sendHello();
  }
}

static void readSerialCommands() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\r') {
      continue;
    }
    if (c == '\n') {
      inputBuffer[inputLength] = '\0';
      handleCommand(inputBuffer);
      inputLength = 0;
    } else if (inputLength < sizeof(inputBuffer) - 1) {
      inputBuffer[inputLength++] = c;
    } else {
      inputLength = 0;  // Linea demasiado larga: se descarta
    }
  }
}

// ---- Botones con anti-rebote ---------------------------------------------
static void scanButtons() {
  unsigned long now = millis();
  for (uint8_t i = 0; i < BUTTON_COUNT; i++) {
    Button &button = buttons[i];
    bool reading = (digitalRead(button.pin) == LOW);  // LOW = presionado (pull-up)

    if (reading != button.lastReading) {
      button.lastReading = reading;
      button.lastChange = now;
    }
    if ((now - button.lastChange) >= DEBOUNCE_MS && reading != button.pressed) {
      button.pressed = reading;
      sendButtonEvent(button, reading);
    }
  }
}

void setup() {
  for (uint8_t i = 0; i < BUTTON_COUNT; i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);
  }
  Serial.begin(BAUD_RATE);
  while (!Serial) {
    ;  // Placas con USB nativo (Leonardo/Micro) esperan a que el PC abra el puerto
  }
  sendHello();
}

void loop() {
  readSerialCommands();
  scanButtons();
}
