# ETAPA 6 — Comunicación Serial con el Arduino

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 6 (última)
> **Prerrequisito:** Etapa 5 completada (sistema en tiempo real funcional)

---

## 1. Objetivo de la etapa

Cerrar el proyecto conectando el sistema en tiempo real de la Etapa 5 con el microcontrolador Arduino, de forma que el ID identificado se transmita por USB-Serial y se manifieste físicamente en los displays de 7 segmentos, LEDs indicadores y buzzer. Al finalizar esta etapa, el proyecto está completo y listo para su defensa.

Al final de esta etapa, el sistema debe poder:

- Ejecutar el bucle completo: hablar → identificar → mostrar en displays físicos.
- Mantener una conexión serial estable entre Python y Arduino.
- Recuperarse automáticamente de desconexiones del USB.
- Verificar la integridad de las tramas mediante checksum.
- Mostrar el ID (0-20) en los dos displays de 7 segmentos.
- Encender el LED indicador correspondiente al estado del sistema.
- Emitir un tono diferenciado según el resultado.

---

## 2. Justificación

Esta es la etapa de **cierre del proyecto**. Todo lo construido hasta ahora era software; aquí el software se convierte en experiencia física tangible.

**Es la etapa que valida la premisa del proyecto.** El enunciado original habla de "reconocimiento de locutores con visualización en display y retroalimentación por microcontrolador". Sin esta etapa, el proyecto sería solo un identificador de audio genérico. Con ella, es un sistema biométrico completo con interfaz hardware.

**Introduce el diseño del protocolo, un concepto central de la asignatura.** El protocolo de comunicación PC ↔ microcontrolador es el corazón de "Arquitectura Aplicada del Computador". Aquí se aplican de forma real conceptos como UART, tramas, checksum, y sincronización entre dispositivos asíncronos.

**Es lo primero que verá el tribunal en la defensa.** Cuando presentas el proyecto, no se ve el código: se ve el circuito físico funcionando. Esta etapa determina la impresión visual final.

**Prueba el sistema completo bajo condiciones reales de uso.** Aparecerán problemas nuevos: interferencias en el cable USB, timing entre subsistemas, ruido eléctrico. Superarlos es prueba de dominio integral del proyecto.

---

## 3. Fundamento teórico

### Protocolo UART sobre USB

**UART (Universal Asynchronous Receiver-Transmitter)** es el protocolo serie más simple: dos hilos (TX y RX) transmiten bytes de 8 bits enmarcados por bits de inicio y parada, a una velocidad acordada (baudios).

Aunque Arduino se conecta por USB, internamente el chip FTDI o ATmega16U2 traduce USB a UART, así que el software se comunica como si fuera un puerto serie clásico.

**Velocidad estándar:** 9600 baudios (~960 bytes/seg) o 115 200 baudios (~11 520 bytes/seg). Como transmitimos 3 bytes por identificación, 9600 baudios son más que suficientes y evitan errores por desincronización.

### Diseño de trama

Una trama es un paquete estructurado que contiene los datos y metadatos para su verificación. Nuestra trama de 3 bytes:

| Byte | Nombre | Valor | Significado |
|---|---|---|---|
| 0 | Cabecera | `0xAA` (170) | Marca de inicio para sincronización |
| 1 | Payload | 0-20 | ID del locutor (0 = desconocido) |
| 2 | Checksum | `0xAA XOR payload` | Verificación de integridad |

**¿Por qué XOR como checksum?** Es rápido de calcular en un microcontrolador (una sola operación), detecta cambios en cualquier bit del payload, y no requiere aritmética multibyte. Suficiente para un canal fiable como USB local.

**¿Por qué 0xAA como cabecera?** Es `10101010` en binario: patrón alternante fácil de reconocer y estadísticamente improbable en ruido.

### Máquina de estados en el firmware

El Arduino lee bytes uno por uno y necesita saber "en qué punto de la trama estoy". Se implementa con una máquina de estados:

1. **ESPERANDO_CABECERA:** ignora bytes hasta encontrar `0xAA`.
2. **ESPERANDO_PAYLOAD:** el siguiente byte es el ID.
3. **ESPERANDO_CHECKSUM:** verifica que el tercer byte coincide con `0xAA XOR ID`.
4. Si es correcto → procesar el ID. Si no → descartar y volver al estado 1.

Esta máquina de estados es defendible en el examen porque es un patrón clásico en sistemas embebidos.

### Comunicación bidireccional (opcional)

El Arduino puede opcionalmente responder con un ACK (acknowledgment) tras recibir cada trama, permitiendo al PC saber que la orden fue recibida. En este proyecto lo dejaremos como mejora opcional.

---

## 4. Decisiones técnicas previas

Se fijan los parámetros de la comunicación:

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Protocolo | **UART sobre USB-Serial** | Estándar de Arduino; nativo en Python con `pyserial`. |
| Velocidad | **9600 baudios** | Suficiente para 3 bytes por identificación; menos susceptible a errores que 115 200. |
| Formato de trama | **3 bytes: [0xAA, ID, XOR]** | Cabecera + payload + checksum. Detecta corrupción. |
| Modo debug | **ASCII en paralelo** | Cuando `DEBUG_SERIAL=True`, también imprime en texto legible. |
| Timeout de lectura | **1 segundo** | Evita bloqueos si el Arduino no responde. |
| Reintentos de reconexión | **Infinitos con delay 2 s** | El programa nunca muere; espera al usuario. |
| Duración del display | **3 segundos** | Tiempo que el ID permanece visible antes de volver al estado "esperando". |
| Frecuencia del buzzer | **1000 Hz reconocido, 500 Hz desconocido** | Tonos diferenciados y agradables. |

---

## 5. Duración estimada

**6 días** de trabajo efectivo (entre 15 y 20 horas en total).

---

## 6. Tareas de la Etapa 6

La etapa se descompone en 8 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 6.1 | Montar el circuito físico en protoboard | 3 h |
| 6.2 | Escribir el firmware básico del Arduino (recepción serial) | 2.5 h |
| 6.3 | Añadir control de displays de 7 segmentos | 2 h |
| 6.4 | Añadir control de LEDs y buzzer | 1.5 h |
| 6.5 | Ampliar `config.py` con parámetros de comunicación serial | 20 min |
| 6.6 | Implementar el módulo Python de comunicación serial | 2.5 h |
| 6.7 | Integrar con el bucle de tiempo real | 1 h |
| 6.8 | Pruebas end-to-end y ajuste fino | 2.5 h |

---

## 7. Desarrollo de cada tarea

### Tarea 6.1 — Montar el circuito físico en protoboard

**Qué hacer:** ensamblar el circuito completo siguiendo el esquema de la sección 5 del documento de exposición. Se recomienda hacerlo por bloques y probar cada uno con el multímetro antes de conectar el siguiente.

**Orden de montaje sugerido (por seguridad):**

**Bloque 1 — Alimentación:**
- Conectar los rieles de 5V y GND de la protoboard al Arduino.
- Verificar con el multímetro que hay 5V estables entre los rieles.

**Bloque 2 — Un LED de prueba:**
- Conectar un LED (con resistencia de 220Ω) al pin D6 y GND.
- Cargar un sketch "Blink" y verificar que parpadea.
- Este paso valida que el Arduino y la protoboard funcionan.

**Bloque 3 — Displays de 7 segmentos con decodificador:**
- Conectar el primer decodificador 74HC4511 al pin D2-D5 del Arduino.
- Conectar los 7 segmentos del display al decodificador con sus resistencias.
- Alimentar el decodificador (VCC y GND).
- Repetir con el segundo display y sus pines D10-D12 (nota: son 4 pines, D10-D13).
- Verificar cableado con multímetro antes de alimentar.

**Bloque 4 — LEDs indicadores:**
- Conectar los 3-4 LEDs a los pines D6, D7, D8, D9 con sus resistencias a GND.

**Bloque 5 — Buzzer:**
- Conectar el buzzer al pin D13 (o al que quede libre) con su resistencia limitadora si es pasivo.

**Verificación final antes de programar:**
- Todos los componentes están alimentados.
- Ningún cable en tensión toca GND.
- El Arduino se enciende sin humo ni calor anormal.

**Nota importante sobre los pines:** los pines exactos pueden variar según tu Arduino. Documenta en un archivo `docs/pinout.md` cuál pin controla qué:

```markdown
# Pinout del Arduino

| Pin      | Componente          |
|----------|---------------------|
| D2-D5    | Decoder BCD decenas |
| D6       | LED verde           |
| D7       | LED rojo            |
| D8       | LED amarillo        |
| D9       | LED azul (opcional) |
| D10-D13  | Decoder BCD unidades|
| A0       | Buzzer              |
```

**Validación de la tarea:** el circuito está montado, no hay cortocircuitos y el Arduino se enciende correctamente.

---

### Tarea 6.2 — Escribir el firmware básico del Arduino (recepción serial)

**Qué hacer:** programar el Arduino para recibir tramas de 3 bytes por el puerto serial e interpretarlas. En esta primera versión, el firmware solo imprime el ID recibido de vuelta (echo) para verificar la comunicación antes de manejar hardware.

**Crear el archivo `arduino/reconocedor_voz/reconocedor_voz.ino`:**

```cpp
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
// Función principal de gestión de un ID válido
// (Se ampliará con hardware en tareas siguientes)
// ============================================================
void procesarID(byte id) {
  Serial.print("[OK] ID recibido: ");
  Serial.println(id);
  // TODO: encender displays, LEDs y buzzer
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
      // Si no es cabecera, se ignora (resincronización automática)
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
  while (!Serial) { ; }   // Esperar al puerto en algunos Arduinos
  Serial.println("[BOOT] Sistema listo. Esperando tramas...");
}

void loop() {
  while (Serial.available() > 0) {
    byte b = Serial.read();
    procesarByteRecibido(b);
  }
}
```

**Cargar el firmware al Arduino** desde el IDE de Arduino.

**Probar con el monitor serial:**

1. Abrir el monitor serial (Ctrl+Shift+M) a 9600 baudios.
2. Configurar el modo "Sin envío de nueva línea".
3. En el modo "Ninguna línea de fin", enviar bytes manualmente en formato hexadecimal si el monitor lo permite.

**Alternativa más fácil: usar un script Python temporal:**

Crear `test_serial.py` en la raíz del proyecto:

```python
import serial
import time

PUERTO = "COM3"   # Ajustar al puerto real (ver Administrador de Dispositivos)
puerto = serial.Serial(PUERTO, 9600, timeout=1)
time.sleep(2)   # Esperar a que Arduino reinicie

# Enviar trama de prueba: ID = 5
CABECERA = 0xAA
ID = 5
checksum = CABECERA ^ ID
trama = bytes([CABECERA, ID, checksum])

print(f"Enviando trama: {trama.hex(' ').upper()}")
puerto.write(trama)

time.sleep(0.5)
respuesta = puerto.read_all().decode('utf-8', errors='replace')
print("Respuesta del Arduino:")
print(respuesta)

puerto.close()
```

Ejecutar:

```bash
python test_serial.py
```

**Validación de la tarea:**
- Al ejecutar `test_serial.py`, la consola muestra `[OK] ID recibido: 5`.
- Modificar el checksum (por ejemplo, sumarle 1) debe hacer que aparezca `[ERR] Checksum inválido`.

---

### Tarea 6.3 — Añadir control de displays de 7 segmentos

**Qué hacer:** ampliar el firmware para que, al recibir un ID, lo muestre en los dos displays de 7 segmentos a través de los decodificadores BCD.

**Modificar `reconocedor_voz.ino`:**

Añadir al inicio, después de las constantes del protocolo:

```cpp
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
```

Añadir estas funciones antes de `procesarID`:

```cpp
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
  // Enviar valor 15 (BCD inválido) → el 74HC4511 apagará todos los segmentos
  escribirDecoder(PIN_DEC_D_A, PIN_DEC_D_B, PIN_DEC_D_C, PIN_DEC_D_D, 15);
  escribirDecoder(PIN_DEC_U_A, PIN_DEC_U_B, PIN_DEC_U_C, PIN_DEC_U_D, 15);
}
```

Modificar `procesarID` para incluir la salida en displays:

```cpp
void procesarID(byte id) {
  Serial.print("[OK] ID recibido: ");
  Serial.println(id);

  mostrarNumero(id);
  delay(DURACION_DISPLAY_MS);
  apagarDisplays();
}
```

Modificar `setup` para inicializar los pines:

```cpp
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

  apagarDisplays();
  Serial.println("[BOOT] Sistema listo. Esperando tramas...");
}
```

**Probar con el script `test_serial.py`** enviando distintos IDs (0, 5, 12, 20).

**Validación de la tarea:**
- Al enviar ID = 5, los displays muestran "05".
- Al enviar ID = 12, muestran "12".
- Al enviar ID = 0, muestran "00".
- Tras 3 segundos, los displays se apagan.

---

### Tarea 6.4 — Añadir control de LEDs y buzzer

**Qué hacer:** completar el firmware con los LEDs de estado y la retroalimentación sonora.

**Añadir al inicio, después de los pines de los decoders:**

```cpp
// LEDs indicadores (ajustar según tu montaje)
const byte PIN_LED_VERDE = 6;      // Reconocido
const byte PIN_LED_ROJO = 7;       // Desconocido
const byte PIN_LED_AMARILLO = 8;   // Procesando (parpadea)

// Buzzer
const byte PIN_BUZZER = 9;
const int FREC_RECONOCIDO = 1000;  // Hz
const int FREC_DESCONOCIDO = 500;  // Hz
const int DURACION_TONO_MS = 200;
```

**Añadir funciones antes de `procesarID`:**

```cpp
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
```

**Modificar `procesarID` para incorporar todo:**

```cpp
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
```

**Añadir en `setup`:**

```cpp
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);
  pinMode(PIN_LED_AMARILLO, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  apagarLEDs();
```

**Probar cada estado:**

```bash
python test_serial.py   # Modificar el ID entre pruebas: 0, 5, 12, 20
```

**Validación de la tarea:**
- Con ID = 0: LED rojo se enciende, buzzer emite tono grave.
- Con ID entre 1 y 20: LED verde se enciende, buzzer emite tono agudo.
- Los displays muestran el ID correcto.
- Tras 3 segundos, todo se apaga.

---

### Tarea 6.5 — Ampliar `config.py` con parámetros de comunicación serial

**Qué hacer:** añadir los parámetros de la conexión serial al archivo de configuración global.

**Añadir al final de `src/config.py`:**

```python
# ============================================================
# COMUNICACIÓN SERIAL CON ARDUINO
# ============================================================
PUERTO_SERIAL = "COM3"                # Windows: COM3, COM4... | Linux: /dev/ttyUSB0
BAUDIOS_SERIAL = 9600
TIMEOUT_SERIAL_S = 1.0
DELAY_RECONEXION_S = 2.0
CABECERA_TRAMA = 0xAA
DEBUG_SERIAL = True                   # Si True, imprime en consola cada envío
```

**Validación de la tarea:** ejecutar `python -c "from src.config import PUERTO_SERIAL; print(PUERTO_SERIAL)"` imprime el puerto configurado.

**Nota:** para averiguar el puerto en Windows, abrir el Administrador de Dispositivos y buscar "Puertos (COM y LPT)". En Linux, ejecutar `ls /dev/ttyUSB*` con el Arduino conectado.

---

### Tarea 6.6 — Implementar el módulo Python de comunicación serial

**Qué hacer:** crear un módulo que gestione la conexión al Arduino, encapsule el envío de tramas con checksum, y maneje reconexiones automáticas.

**Crear el archivo `src/serial_comm.py`:**

```python
"""
Módulo de comunicación serial con el microcontrolador.
Gestiona el envío de tramas con checksum y la reconexión automática.
"""

import time
import serial
from serial.serialutil import SerialException
from typing import Optional

from src.config import (
    PUERTO_SERIAL,
    BAUDIOS_SERIAL,
    TIMEOUT_SERIAL_S,
    DELAY_RECONEXION_S,
    CABECERA_TRAMA,
    DEBUG_SERIAL,
)


class ComunicacionArduino:
    """
    Cliente serial hacia el Arduino con reconexión automática.
    """

    def __init__(self, puerto: str = None, baudios: int = None):
        self.puerto_nombre = puerto or PUERTO_SERIAL
        self.baudios = baudios or BAUDIOS_SERIAL
        self.puerto: Optional[serial.Serial] = None

    def conectar(self) -> bool:
        """
        Intenta abrir el puerto serial.
        Retorna True si se establece la conexión, False en caso contrario.
        """
        try:
            self.puerto = serial.Serial(
                port=self.puerto_nombre,
                baudrate=self.baudios,
                timeout=TIMEOUT_SERIAL_S,
            )
            time.sleep(2)   # El Arduino se reinicia al abrir el puerto
            if DEBUG_SERIAL:
                print(f"[Serial] Conectado a {self.puerto_nombre} @ {self.baudios} bps")
            return True
        except SerialException as e:
            if DEBUG_SERIAL:
                print(f"[Serial] Error al conectar: {e}")
            self.puerto = None
            return False

    def desconectar(self):
        """Cierra el puerto serial si está abierto."""
        if self.puerto and self.puerto.is_open:
            self.puerto.close()
            if DEBUG_SERIAL:
                print("[Serial] Desconectado.")
        self.puerto = None

    def esta_conectado(self) -> bool:
        return self.puerto is not None and self.puerto.is_open

    def enviar_id(self, id_locutor: int) -> bool:
        """
        Envía un ID al Arduino en formato de trama de 3 bytes.

        Trama: [cabecera=0xAA, id, checksum=cabecera XOR id]

        Retorna True si el envío fue exitoso.
        """
        if not (0 <= id_locutor <= 20):
            raise ValueError(f"ID debe estar entre 0 y 20, recibido: {id_locutor}")

        if not self.esta_conectado():
            if not self.conectar():
                return False

        checksum = CABECERA_TRAMA ^ id_locutor
        trama = bytes([CABECERA_TRAMA, id_locutor, checksum])

        try:
            self.puerto.write(trama)
            if DEBUG_SERIAL:
                print(f"[Serial] Enviado: {' '.join(f'{b:02X}' for b in trama)} "
                      f"(ID={id_locutor})")
            return True
        except SerialException as e:
            if DEBUG_SERIAL:
                print(f"[Serial] Error al enviar: {e}. Reintentando en {DELAY_RECONEXION_S}s...")
            self.desconectar()
            time.sleep(DELAY_RECONEXION_S)
            return False

    def leer_respuesta(self, max_espera_ms: int = 500) -> str:
        """
        Lee la respuesta ASCII del Arduino durante max_espera_ms milisegundos.
        Útil para depuración.
        """
        if not self.esta_conectado():
            return ""

        buffer = b""
        deadline = time.time() + max_espera_ms / 1000
        while time.time() < deadline:
            n = self.puerto.in_waiting
            if n > 0:
                buffer += self.puerto.read(n)
            else:
                time.sleep(0.01)
        return buffer.decode("utf-8", errors="replace")


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enviar un ID al Arduino por serial.")
    parser.add_argument("id", type=int, help="ID a enviar (0-20).")
    parser.add_argument("--puerto", type=str, default=None, help="Puerto serial.")
    args = parser.parse_args()

    arduino = ComunicacionArduino(puerto=args.puerto)
    if arduino.conectar():
        arduino.enviar_id(args.id)
        respuesta = arduino.leer_respuesta(800)
        if respuesta.strip():
            print(f"[Arduino] {respuesta}")
        arduino.desconectar()
    else:
        print("No se pudo conectar al Arduino.")
```

**Ejecutar prueba de envío:**

```bash
python -m src.serial_comm 7
```

**Validación de la tarea:**
- La consola muestra `[Serial] Enviado: AA 07 AD (ID=7)`.
- El Arduino responde `[OK] ID recibido: 7`.
- Los displays muestran "07", el LED verde se enciende y el buzzer suena.

---

### Tarea 6.7 — Integrar con el bucle de tiempo real

**Qué hacer:** modificar `tiempo_real.py` para que, además de mostrar el ID en consola, lo envíe al Arduino a través del módulo serial.

**Modificar `src/tiempo_real.py`:**

Añadir la importación al inicio:

```python
from src.serial_comm import ComunicacionArduino
```

Modificar la clase `SistemaTiempoReal`. En `__init__`, añadir la inicialización del Arduino:

```python
def __init__(self):
    print("Cargando identificador y modelos...")
    self.identificador = Identificador(verbose=False)
    self.detector = DetectorEnunciados(callback=self._al_detectar_enunciado)
    self.contador = 0

    print(f"  {len(self.identificador.modelos)} locutores cargados.")
    print(f"  Umbral de decisión: {self.identificador.umbral:.3f}")

    # Conexión al Arduino
    print("\nConectando al Arduino...")
    self.arduino = ComunicacionArduino()
    if self.arduino.conectar():
        print("  Arduino conectado.")
    else:
        print("  AVISO: Arduino no disponible. El sistema funcionará solo en consola.")

    print()
```

Modificar `_al_detectar_enunciado` para enviar el ID al Arduino:

```python
def _al_detectar_enunciado(self, audio: np.ndarray):
    """Callback llamado cada vez que el detector encuentra un enunciado."""
    self.contador += 1
    duracion = len(audio) / FRECUENCIA_MUESTREO

    t0 = time.time()
    resultado = self.identificador.identificar_audio(audio)
    t_proceso = time.time() - t0

    if resultado.es_desconocido:
        etiqueta = "DESCONOCIDO"
        id_output = 0
        color = "\033[93m"
    else:
        etiqueta = f"LOCUTOR {resultado.id_predicho:02d}"
        id_output = resultado.id_predicho
        color = "\033[92m"

    reset = "\033[0m"

    print(
        f"[Enunciado #{self.contador:03d}] "
        f"duración={duracion:.2f}s | "
        f"procesado en {t_proceso*1000:.0f}ms | "
        f"LLR={resultado.llr_maximo:+.3f}"
    )
    print(f"{color}  →  ID = {id_output:02d}  ({etiqueta}){reset}")

    # Enviar al Arduino
    if self.arduino.esta_conectado():
        exito = self.arduino.enviar_id(id_output)
        if not exito:
            print(f"  [AVISO] No se pudo enviar al Arduino, se intentará reconectar.")

    print()
```

Añadir cierre limpio en `iniciar`:

```python
def iniciar(self):
    print("=" * 60)
    print("  SISTEMA DE IDENTIFICACIÓN DE VOZ EN TIEMPO REAL")
    print("=" * 60)
    print()
    print("Habla al micrófono. El sistema identificará al locutor")
    print("y mostrará el resultado en los displays físicos.")
    print("Pulsa Ctrl+C para detener.")
    print()

    try:
        self.detector.escuchar()
    finally:
        self.arduino.desconectar()
```

**Ejecutar el sistema completo:**

```bash
python -m src.tiempo_real
```

**Validación de la tarea:** cuando alguien habla:
1. El sistema detecta el enunciado.
2. Identifica al locutor.
3. Muestra el ID en consola.
4. Envía el ID al Arduino.
5. El Arduino muestra el ID en los displays.
6. Se enciende el LED verde (registrado) o rojo (desconocido).
7. Suena el buzzer con el tono correspondiente.
8. Tras 3 segundos, todo vuelve al estado de espera.

---

### Tarea 6.8 — Pruebas end-to-end y ajuste fino

**Qué hacer:** una vez integrado todo el sistema, hacer una batería de pruebas exhaustiva para detectar y corregir los últimos problemas.

**Batería de pruebas end-to-end:**

**Prueba 1 — Reconocimiento normal**
Cada locutor registrado habla 5 veces. Verificar que el display muestra el ID correcto en al menos 4/5 casos.

**Prueba 2 — Rechazo de desconocidos**
Una persona no registrada habla 5 veces. Verificar que se muestra "00" y se enciende el LED rojo en al menos 3/5 casos.

**Prueba 3 — Robustez a desconexiones**
Con el sistema funcionando, desconectar el cable USB del Arduino. Verificar que:
- El programa Python NO se cuelga.
- Aparecen mensajes de aviso.
- Al reconectar el USB, el sistema retoma automáticamente los envíos.

**Prueba 4 — Latencia total**
Medir con cronómetro el tiempo entre "termina de hablar" y "el display muestra el ID". Debe ser < 1.5 segundos.

**Prueba 5 — Estabilidad prolongada**
Dejar el sistema funcionando 10 minutos, hablando cada 30 segundos. Verificar que:
- No hay fugas de memoria (el programa no se ralentiza).
- No hay bloqueos ni excepciones.
- El Arduino responde consistentemente.

**Prueba 6 — Envíos rápidos consecutivos**
Hablar varias frases seguidas sin pausa. Verificar que el Arduino procesa todas las tramas sin perderse ni corromperse.

**Documentar los resultados** en `docs/pruebas_finales.md`. Este documento va a la memoria.

**Validación final de la etapa:** las 6 pruebas se superan con los criterios indicados.

---

## 8. Entregables de la Etapa 6

Al finalizar esta etapa se debe contar con:

- Circuito físico montado, cableado y funcional.
- Firmware `arduino/reconocedor_voz/reconocedor_voz.ino` completo.
- Documento `docs/pinout.md` con la asignación de pines.
- Ampliación de `src/config.py` con parámetros de comunicación serial.
- Módulo `src/serial_comm.py` con la clase `ComunicacionArduino`.
- Integración en `src/tiempo_real.py` con envío al Arduino.
- Documento `docs/pruebas_finales.md` con los resultados de la batería end-to-end.
- **Vídeo demo del sistema completo funcionando** (indispensable para la defensa).
- Commit final en GitHub con el mensaje "Etapa 6 completada: proyecto finalizado".
- Etiqueta de release en GitHub: `v1.0-defensa`.

---

## 9. Checklist de validación de la etapa

Antes de considerar el proyecto finalizado, verificar:

- [ ] `python -m src.serial_comm 5` envía correctamente y el Arduino responde.
- [ ] Todos los IDs 0-20 se muestran correctamente en los displays.
- [ ] Los LEDs verde y rojo funcionan según el estado (registrado/desconocido).
- [ ] El buzzer emite tonos diferenciados.
- [ ] `python -m src.tiempo_real` ejecuta el sistema completo end-to-end.
- [ ] Al desconectar y reconectar el Arduino, el sistema se recupera automáticamente.
- [ ] La latencia total es < 1.5 segundos.
- [ ] El sistema funciona ininterrumpidamente durante al menos 10 minutos.
- [ ] El vídeo demo está grabado (recomendado: 60-90 segundos).
- [ ] El repositorio está actualizado y etiquetado con `v1.0-defensa`.

---

## 10. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| No detecta el puerto COM | Driver del Arduino no instalado | Instalar drivers CH340 o FTDI (según Arduino). |
| `SerialException: could not open port` | Puerto ocupado por el IDE de Arduino | Cerrar el monitor serial del IDE. |
| El Arduino reinicia al conectar | Comportamiento normal | Añadir `time.sleep(2)` tras `conectar()` (ya incluido). |
| Los displays muestran valores aleatorios | Mala conexión del decodificador | Revisar cableado con multímetro; buscar contactos flojos. |
| Un segmento del display no enciende | Resistencia quemada o conexión mala | Sustituir la resistencia; verificar continuidad. |
| El buzzer no suena | Pin PWM incorrecto para `tone()` | En Arduino UNO, no usar pines 3, 11 con `tone()` si también hay librería `Servo`. |
| El sistema se cuelga tras un rato | Buffer serial saturado | Añadir `puerto.flushInput()` periódicamente. |
| Los caracteres en respuesta del Arduino se ven raros | Velocidad de baudios distinta en Python y firmware | Verificar que ambos usan 9600 (o el mismo valor). |
| El ID enviado no coincide con el mostrado | Endianness o cast incorrecto | Verificar que se envía `bytes([...])`, no strings. |

---

## 11. Recomendaciones adicionales

**Para la memoria y defensa:**

- El **vídeo demo del sistema completo** es el activo más importante de la defensa. Debe mostrar: varios locutores registrados siendo reconocidos, un desconocido siendo rechazado, y una vista del hardware respondiendo. Duración recomendada: 60-90 segundos.
- Incluir en la memoria un **diagrama de secuencia** que muestre el flujo: usuario habla → Python detecta → identifica → envía trama → Arduino procesa → activa hardware. Este tipo de diagrama es muy valorado por los tribunales.
- Preparar una **tabla comparativa antes/después** por etapa: sin sistema (proceso manual), con software (Etapa 5), con hardware (Etapa 6). Muestra la progresión del valor añadido.

**Para la defensa oral:**

- Empezar la demostración con el hardware YA funcionando. Pedir a un miembro del tribunal (si acepta) que se acerque al micrófono y diga la frase. El "efecto sorpresa" de rechazarlo como desconocido genera muy buena impresión.
- Preparar respuestas para preguntas técnicas típicas:
  - *"¿Por qué usó UART y no I2C o SPI?"* → UART es punto a punto entre PC y Arduino, no requiere buses complejos y es el estándar de facto para depuración.
  - *"¿Por qué XOR como checksum y no CRC?"* → Coste computacional mínimo en el microcontrolador y suficiente para detectar corrupciones en un canal fiable como USB local. CRC-8 sería el paso lógico siguiente si se detectaran errores.
  - *"¿Cómo escalaría a más de 20 locutores?"* → El protocolo actual usa 1 byte para el ID (rango 0-255), así que soporta hasta 255 sin cambios. El límite real es el número de dígitos del display; con 3 displays llegaríamos a 999.

**Sobre el cierre del proyecto:**

- Etiquetar la versión final en GitHub como `v1.0-defensa` para tener un punto de referencia inmutable.
- Escribir un **README final del proyecto** que resuma qué hace, cómo se instala, cómo se ejecuta, y los resultados obtenidos.
- Considerar añadir una sección de **trabajo futuro** en la memoria: soporte multilocutor simultáneo, migración a Raspberry Pi para independencia de PC, VAD por deep learning, aumentación de datos por técnicas de speed perturbation.

---

## 12. Cierre del proyecto

Con la finalización de esta etapa, **el proyecto está completo**.

Resumen de lo construido a lo largo de las 7 etapas (0 a 6):

- **Etapa 0:** entorno reproducible con Python, entorno virtual, y repositorio Git.
- **Etapa 1:** captura de audio con calidad estandarizada.
- **Etapa 2:** extracción de características MFCC con preprocesamiento robusto.
- **Etapa 3:** entrenamiento de modelos GMM + UBM.
- **Etapa 4:** identificación con LLR, umbral calibrado y matriz de confusión.
- **Etapa 5:** funcionamiento en tiempo real con VAD por energía.
- **Etapa 6:** conexión con Arduino y salida física por displays, LEDs y buzzer.

**Enhorabuena por completar un proyecto técnico integral** que combina procesamiento digital de señales, aprendizaje estadístico, programación embebida y diseño de protocolos. Este trabajo demuestra dominio de todo el ciclo de vida de un sistema, desde la teoría hasta la implementación física, y es un excelente ejemplo de lo que se espera al final de una asignatura como Arquitectura Aplicada del Computador.

Toca ahora preparar la defensa. Éxito.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
