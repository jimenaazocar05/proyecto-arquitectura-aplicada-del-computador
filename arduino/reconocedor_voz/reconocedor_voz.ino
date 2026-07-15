/*
 * Sistema de Identificación de Voces Humanas — Firmware
 * Proyecto de Arquitectura Aplicada del Computador
 *
 * Recibe por Serial una trama de 3 bytes: [0xAA, ID, checksum]
 * y activa los indicadores físicos según el ID.
 */

// ============================================================
// Constantes del protocolo
// ============================================================
const byte CABECERA = 0xAA;
const unsigned long BAUDIOS = 9600;

// ============================================================
// Pines del hardware
// ============================================================
// Decoder BCD para decenas (pines D2-D5 = bits A, B, C, D)
const byte PIN_DEC_D_A = 2;
const byte PIN_DEC_D_B = 3;
const byte PIN_DEC_D_C = 4;
const byte PIN_DEC_D_D = 5;

// Decoder BCD para unidades (pines D10-D13 = bits A, B, C, D)
const byte PIN_DEC_U_A = 10;
const byte PIN_DEC_U_B = 11;
const byte PIN_DEC_U_C = 12;
const byte PIN_DEC_U_D = 13;

// Duración que el ID permanece visible
const unsigned long DURACION_DISPLAY_MS = 3000;

// LEDs indicadores
const byte PIN_LED_VERDE = 6;      // Reconocido
const byte PIN_LED_ROJO = 7;       // Desconocido
const byte PIN_LED_AMARILLO = 8;   // Procesando (parpadea)

// Buzzer
const byte PIN_BUZZER = 9;
const int FREC_RECONOCIDO = 1000;  // Hz
const int FREC_DESCONOCIDO = 500;  // Hz
const int DURACION_TONO_MS = 200;

// ============================================================
// Estados de la máquina de recepción
// ============================================================
enum EstadoRx {
  ESPERANDO_CABECERA,
  ESPERANDO_PAYLOAD,
  ESPERANDO_CHECKSUM
};

EstadoRx estado = ESPERANDO_CABECERA;
byte payload_recibido = 0;

// ============================================================
// Control de los displays
// ============================================================
void escribirDecoder(byte pinA, byte pinB, byte pinC, byte pinD, byte digito) {
  // Descompone el dígito (0-9) en sus 4 bits BCD
  digitalWrite(pinA, digito & 0b0001);
  digitalWrite(pinB, (digito >> 1) & 0b0001);
  digitalWrite(pinC, (digito >> 2) & 0b0001);
  digitalWrite(pinD, (digito >> 3) & 0b0001);
}

void mostrarNumero(byte n) {
  byte decenas = n / 10;
  byte unidades = n % 10;
  escribirDecoder(PIN_DEC_D_A, PIN_DEC_D_B, PIN_DEC_D_C, PIN_DEC_D_D, decenas);
  escribirDecoder(PIN_DEC_U_A, PIN_DEC_U_B, PIN_DEC_U_C, PIN_DEC_U_D, unidades);
}

void apagarDisplays() {
  // Enviar valor 15 (BCD inválido) -> el 74HC4511 apagará todos los segmentos
  escribirDecoder(PIN_DEC_D_A, PIN_DEC_D_B, PIN_DEC_D_C, PIN_DEC_D_D, 15);
  escribirDecoder(PIN_DEC_U_A, PIN_DEC_U_B, PIN_DEC_U_C, PIN_DEC_U_D, 15);
}

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
// Función principal de gestión de un ID válido
// ============================================================
void procesarID(byte id) {
  Serial.print("[OK] ID recibido: ");
  Serial.println(id);

  mostrarNumero(id);

  if (id == 0) {
    indicarDesconocido();
  } else {
    indicarReconocido();
  }

  delay(DURACION_DISPLAY_MS);
  apagarDisplays();
  apagarLEDs();
}

// ============================================================
// Máquina de recepción por byte
// ============================================================
void procesarByteRecibido(byte b) {
  switch (estado) {
    case ESPERANDO_CABECERA:
      if (b == CABECERA) {
        estado = ESPERANDO_PAYLOAD;
      }
      break;

    case ESPERANDO_PAYLOAD:
      payload_recibido = b;
      estado = ESPERANDO_CHECKSUM;
      break;

    case ESPERANDO_CHECKSUM:
      byte checksum_esperado = CABECERA ^ payload_recibido;
      if (b == checksum_esperado) {
        procesarID(payload_recibido);
      } else {
        Serial.print("[ERR] Checksum inválido. Payload=");
        Serial.print(payload_recibido);
        Serial.print(" recibido=");
        Serial.print(b);
        Serial.print(" esperado=");
        Serial.println(checksum_esperado);
      }
      estado = ESPERANDO_CABECERA;
      break;
  }
}

// ============================================================
// Setup y loop
// ============================================================
void setup() {
  Serial.begin(BAUDIOS);
  while (!Serial) { ; }

  // Configurar pines de los decoders como salidas
  pinMode(PIN_DEC_D_A, OUTPUT);
  pinMode(PIN_DEC_D_B, OUTPUT);
  pinMode(PIN_DEC_D_C, OUTPUT);
  pinMode(PIN_DEC_D_D, OUTPUT);
  pinMode(PIN_DEC_U_A, OUTPUT);
  pinMode(PIN_DEC_U_B, OUTPUT);
  pinMode(PIN_DEC_U_C, OUTPUT);
  pinMode(PIN_DEC_U_D, OUTPUT);

  // Configurar LEDs y Buzzer
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);
  pinMode(PIN_LED_AMARILLO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  apagarDisplays();
  apagarLEDs();

  Serial.println("[BOOT] Sistema listo. Esperando tramas...");
}

void loop() {
  while (Serial.available() > 0) {
    byte b = Serial.read();
    procesarByteRecibido(b);
  }
}
