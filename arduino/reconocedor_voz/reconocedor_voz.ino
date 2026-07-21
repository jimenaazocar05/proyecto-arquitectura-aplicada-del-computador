/*
 * Sistema de Identificacion de Voces Humanas -- Firmware
 * Proyecto de Arquitectura Aplicada del Computador
 *
 * Recibe por Serial una trama de 3 bytes: [0xAA, ID, checksum]
 * y activa LEDs y buzzer segun el ID.
 * El ID numerico se muestra en la interfaz web.
 *
 * Version no-bloqueante: usa millis() en lugar de delay()
 * para evitar saturar el buffer serial del Arduino Uno.
 */

// ============================================================
// Constantes del protocolo
// ============================================================
const byte CABECERA = 0xAA;
const unsigned long BAUDIOS = 9600;

// ============================================================
// Pines del hardware
// ============================================================
const byte PIN_LED_VERDE = 6;
const byte PIN_LED_ROJO = 7;
const byte PIN_LED_AMARILLO = 8;
const byte PIN_BUZZER = 9;

// Temporizacion
const unsigned long DURACION_LED_PROCESANDO_MS = 300;
const unsigned long DURACION_RESULTADO_MS = 3000;
const int FREC_RECONOCIDO = 1000;
const int FREC_DESCONOCIDO = 500;
const int DURACION_TONO_MS = 200;

// ============================================================
// Estados del sistema (no-bloqueante)
// ============================================================
enum EstadoSistema {
  ESPERANDO,
  LED_AMARILLO,
  MOSTRANDO_RESULTADO
};

EstadoSistema estado_sistema = ESPERANDO;
byte ultimo_id = 0;
unsigned long tiempo_cambio_estado = 0;

// ============================================================
// Estados de la maquina de recepcion serial
// ============================================================
enum EstadoRx {
  ESPERANDO_CABECERA,
  ESPERANDO_PAYLOAD,
  ESPERANDO_CHECKSUM
};

EstadoRx estado_rx = ESPERANDO_CABECERA;
byte payload_recibido = 0;

// ============================================================
// Control de LEDs y buzzer
// ============================================================
void apagarLEDs() {
  digitalWrite(PIN_LED_VERDE, LOW);
  digitalWrite(PIN_LED_ROJO, LOW);
  digitalWrite(PIN_LED_AMARILLO, LOW);
}

void indicarReconocido() {
  apagarLEDs();
  digitalWrite(PIN_LED_VERDE, HIGH);
  tone(PIN_BUZZER, FREC_RECONOCIDO, DURACION_TONO_MS);
}

void indicarDesconocido() {
  apagarLEDs();
  digitalWrite(PIN_LED_ROJO, HIGH);
  tone(PIN_BUZZER, FREC_DESCONOCIDO, DURACION_TONO_MS);
}

// ============================================================
// Recepcion serial por bytes (no-bloqueante)
// ============================================================
void procesarByteRecibido(byte b) {
  switch (estado_rx) {
    case ESPERANDO_CABECERA:
      if (b == CABECERA) {
        estado_rx = ESPERANDO_PAYLOAD;
      }
      break;

    case ESPERANDO_PAYLOAD:
      payload_recibido = b;
      estado_rx = ESPERANDO_CHECKSUM;
      break;

    case ESPERANDO_CHECKSUM:
      byte checksum_esperado = CABECERA ^ payload_recibido;
      if (b == checksum_esperado) {
        // Recibimos un ID valido — iniciar secuencia inmediatamente
        ultimo_id = payload_recibido;
        Serial.print("[OK] ID recibido: ");
        Serial.println(ultimo_id);

        encenderLEDAmarillo();
      } else {
        Serial.print("[ERR] Checksum invalido. Payload=");
        Serial.print(payload_recibido);
        Serial.print(" recibido=");
        Serial.print(b);
        Serial.print(" esperado=");
        Serial.println(checksum_esperado);
      }
      estado_rx = ESPERANDO_CABECERA;
      break;
  }
}

// ============================================================
// Funciones del bucle no-bloqueante
// ============================================================
void encenderLEDAmarillo() {
  apagarLEDs();
  digitalWrite(PIN_LED_AMARILLO, HIGH);
  estado_sistema = LED_AMARILLO;
  tiempo_cambio_estado = millis();
}

void mostrarResultado(byte id) {
  if (id == 0) {
    indicarDesconocido();
  } else {
    indicarReconocido();
  }
  estado_sistema = MOSTRANDO_RESULTADO;
  tiempo_cambio_estado = millis();
}

// ============================================================
// Setup y loop
// ============================================================
void setup() {
  Serial.begin(BAUDIOS);
  while (!Serial) { ; }

  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);
  pinMode(PIN_LED_AMARILLO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  apagarLEDs();
  Serial.println("[BOOT] Sistema listo. Esperando tramas...");
}

void loop() {
  // 1. Procesar bytes seriales en cada iteracion (NUNCA se bloquea)
  while (Serial.available() > 0) {
    byte b = Serial.read();
    procesarByteRecibido(b);
  }

  // 2. Maquina de estados del sistema (no-bloqueante)
  unsigned long ahora = millis();

  switch (estado_sistema) {

    case LED_AMARILLO:
      if (ahora - tiempo_cambio_estado >= DURACION_LED_PROCESANDO_MS) {
        mostrarResultado(ultimo_id);
      }
      break;

    case MOSTRANDO_RESULTADO:
      if (ahora - tiempo_cambio_estado >= DURACION_RESULTADO_MS) {
        apagarLEDs();
        estado_sistema = ESPERANDO;
      }
      break;

    case ESPERANDO:
      // No hacer nada, solo esperar la proxima trama
      break;
  }
}
