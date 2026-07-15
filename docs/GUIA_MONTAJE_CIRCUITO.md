# GUÍA DE MONTAJE — Circuito Físico Simplificado

> **Proyecto:** Sistema de Identificación de Voces Humanas
> **Configuración adoptada:** LEDs + Buzzer en hardware, ID en interfaz web
> **Duración estimada:** 1.5 - 2 horas

---

## 1. Componentes necesarios

Verifica que dispones de todos estos componentes antes de empezar:

| Cantidad | Componente | Especificación |
|---|---|---|
| 1 | Arduino UNO | Con cable USB tipo B |
| 1 | Protoboard | Estándar (400+ puntos) |
| 1 | LED verde | 5 mm, cualquier voltaje típico (2V) |
| 1 | LED rojo | 5 mm |
| 1 | LED amarillo | 5 mm |
| 1 | Buzzer | Pasivo o activo (idealmente pasivo para tonos variables) |
| 3 | Resistencias | 220Ω (código: rojo-rojo-marrón-dorado) |
| 8-10 | Cables jumper | Macho-macho, colores variados |

**Nota sobre los LEDs:** cada LED tiene una pata larga (ánodo, +) y una corta (cátodo, -). La pata larga va al pin del Arduino, la corta al riel negativo.

---

## 2. Diagrama de conexiones

Este es el mapa que vamos a construir:

```
Arduino UNO                        Protoboard
─────────────                      ─────────────
Pin D6  ────► [Resistencia 220Ω] ────► LED VERDE  ────► GND
Pin D7  ────► [Resistencia 220Ω] ────► LED ROJO   ────► GND
Pin D8  ────► [Resistencia 220Ω] ────► LED AMARILLO ──► GND
Pin D9  ────► BUZZER ────────────────────────────────► GND
GND     ────► Riel negativo de la protoboard
```

**Pinout resumido:**

| Pin Arduino | Función |
|---|---|
| D6 | LED verde (reconocido) |
| D7 | LED rojo (desconocido) |
| D8 | LED amarillo (procesando) |
| D9 | Buzzer |
| GND | Tierra común |

---

## 3. Montaje paso a paso

### Paso 1 — Preparar la protoboard

**Objetivo:** conectar el riel negativo (GND) de la protoboard al pin GND del Arduino.

1. Toma un cable jumper (preferiblemente negro por convención).
2. Conecta un extremo al pin **GND** del Arduino (hay varios pines GND; usa el que esté cerca de "POWER").
3. Conecta el otro extremo al **riel negativo (-)** de la protoboard (columna con línea azul o negra).

**Verificación:** el riel negativo ahora es la tierra común de todo el circuito.

**Nota importante sobre la protoboard:** los dos rieles verticales de cada lado (con marcas + y -) están conectados internamente a lo largo de toda su columna. Las filas horizontales numeradas (1, 2, 3...) están conectadas entre columnas a-e y f-j, pero NO se cruzan por el medio.

---

### Paso 2 — Montar el LED verde (locutor reconocido)

**Objetivo:** conectar el LED verde al pin D6 con su resistencia limitadora.

1. Inserta la **resistencia de 220Ω** entre dos puntos de la protoboard (por ejemplo, fila 5 columnas e y f).
2. Inserta el **LED verde**:
   - Pata larga (ánodo, +): en la misma fila donde termina la resistencia (columna g, fila 5).
   - Pata corta (cátodo, -): en una fila más abajo (fila 6 o 7).
3. Conecta con un cable jumper el **cátodo del LED** al **riel negativo (-)** de la protoboard.
4. Conecta con otro cable jumper el **inicio de la resistencia** (fila 5, columna e) al pin **D6** del Arduino.

**Prueba parcial (opcional pero recomendada):**

Antes de continuar, puedes verificar que este LED funciona. Carga temporalmente en el Arduino este sketch de prueba:

```cpp
void setup() {
  pinMode(6, OUTPUT);
}
void loop() {
  digitalWrite(6, HIGH);
  delay(500);
  digitalWrite(6, LOW);
  delay(500);
}
```

El LED verde debe parpadear cada segundo. Si funciona, apaga el Arduino y continúa con el LED rojo.

---

### Paso 3 — Montar el LED rojo (locutor desconocido)

Repite exactamente el mismo procedimiento que el LED verde, pero:

- Usa **filas 9-11** de la protoboard (para separación visual del LED verde).
- Conecta el ánodo (a través de la resistencia) al pin **D7** del Arduino.
- El cátodo va al mismo riel negativo (-).

---

### Paso 4 — Montar el LED amarillo (procesando)

Igual que los anteriores:

- Usa **filas 13-15** de la protoboard.
- Conecta el ánodo (a través de la resistencia) al pin **D8** del Arduino.
- El cátodo va al riel negativo (-).

**Verificación general antes de continuar:**

Carga este sketch temporal para probar los 3 LEDs a la vez:

```cpp
void setup() {
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
}
void loop() {
  digitalWrite(6, HIGH); delay(400); digitalWrite(6, LOW);
  digitalWrite(7, HIGH); delay(400); digitalWrite(7, LOW);
  digitalWrite(8, HIGH); delay(400); digitalWrite(8, LOW);
}
```

Los tres LEDs deben encenderse en secuencia: verde → rojo → amarillo → verde...

Si alguno no enciende, revisar:
- Polaridad del LED (¿pata larga hacia la resistencia?).
- Conexión de la resistencia (¿ambos extremos en fila correcta?).
- Cable al pin del Arduino (¿pin correcto?).
- Riel negativo conectado al GND del Arduino.

---

### Paso 5 — Montar el buzzer

**Los buzzers vienen en dos tipos y se montan diferente. Identifica el tuyo:**

- **Buzzer activo:** suele tener una etiqueta y produce un tono fijo al recibir 5V.
- **Buzzer pasivo:** más pequeño, sin etiqueta usualmente, produce tonos variables según la frecuencia PWM.

**Para ambos tipos, el montaje es el mismo:**

1. Identifica las patillas: el buzzer tiene **dos patillas**, una marcada con `+` (positivo) y otra sin marca (negativo/GND).
2. Inserta el buzzer en la protoboard en las **filas 18-19**.
3. Conecta la **patilla positiva (+)** al pin **D9** del Arduino con un cable jumper.
4. Conecta la **patilla negativa** al **riel negativo (-)** de la protoboard.

**No necesita resistencia**, el buzzer maneja bien los 5V directos del Arduino.

**Verificación del buzzer:**

```cpp
void setup() {
  pinMode(9, OUTPUT);
}
void loop() {
  tone(9, 1000);   // 1000 Hz
  delay(500);
  noTone(9);
  delay(500);
}
```

El buzzer debe pitar cada segundo. Si no suena:
- Verifica polaridad (patilla +).
- Si es buzzer activo, el `tone()` puede no funcionar; prueba con `digitalWrite(9, HIGH)`.

---

## 4. Ajuste del firmware

Como cambiamos la asignación de pines respecto al plan original (ya no hay displays), necesitamos verificar que el firmware coincida con este montaje.

**Abrir `arduino/reconocedor_voz/reconocedor_voz.ino` y verificar/ajustar** estas constantes:

```cpp
// LEDs indicadores
const byte PIN_LED_VERDE = 6;      // Reconocido
const byte PIN_LED_ROJO = 7;       // Desconocido
const byte PIN_LED_AMARILLO = 8;   // Procesando

// Buzzer
const byte PIN_BUZZER = 9;
```

**Como ahora NO hay displays, hay dos opciones:**

### Opción A — Dejar el firmware como está

Los pines D2-D5 y D10-D13 (que antes iban a los decodificadores) simplemente no tendrán nada conectado. No pasa nada, solo estarán inactivos. Es la opción más simple.

### Opción B — Limpiar el firmware (recomendado)

Eliminar del firmware todo el código relacionado con displays, ya que no se usará. Esto hace el código más limpio y explicable en la defensa.

**Buscar y eliminar del firmware las siguientes secciones:**

1. Las constantes `PIN_DEC_D_A` a `PIN_DEC_U_D`.
2. La función `escribirDecoder()`.
3. La función `mostrarNumero()`.
4. La función `apagarDisplays()`.
5. Las llamadas a `mostrarNumero(id)` y `apagarDisplays()` en `procesarID`.
6. Los `pinMode` de los pines de los decodificadores en `setup()`.

**El `procesarID` quedará así (más limpio):**

```cpp
void procesarID(byte id) {
  Serial.print("[OK] ID recibido: ");
  Serial.println(id);

  if (id == 0) {
    indicarDesconocido();
  } else {
    indicarReconocido();
  }

  delay(DURACION_DISPLAY_MS);
  apagarLEDs();
}
```

Recompilar y cargar el firmware al Arduino tras hacer los cambios.

---

## 5. Prueba integral del hardware

Con el firmware ya cargado, ejecuta desde la consola:

```bash
python test_serial.py
```

**Debe ocurrir lo siguiente:**

1. El script envía el ID = 5 al Arduino.
2. El Arduino recibe la trama con checksum correcto.
3. Se enciende el LED **verde** (porque 5 ≠ 0, es un locutor registrado).
4. El buzzer emite un tono agudo (~1000 Hz).
5. Tras 3 segundos, el LED se apaga y el buzzer para.

**Modificar `test_serial.py` para probar el ID = 0** (desconocido):

```python
ID = 0   # Cambiar de 5 a 0
```

Ejecutar de nuevo. Ahora debe encenderse el LED **rojo** y sonar un tono grave (~500 Hz).

---

## 6. Prueba end-to-end del sistema completo

Con el hardware validado, ejecuta el sistema completo:

```bash
python -m src.tiempo_real
```

**Flujo esperado:**

1. Al arrancar, la consola muestra "Arduino conectado".
2. Habla al micrófono diciendo «Mi voz es mi clave».
3. La consola muestra el ID identificado.
4. El Arduino recibe la trama.
5. Se enciende el LED correspondiente (verde si reconocido, rojo si desconocido).
6. Suena el buzzer con el tono correspondiente.
7. Tras 3 segundos, todo se apaga y el sistema queda listo para el siguiente enunciado.

---

## 7. Checklist de validación del hardware

Antes de pasar al frontend web, verifica:

- [ ] Los 3 LEDs encienden individualmente con el sketch de prueba.
- [ ] El buzzer emite tonos con el sketch de prueba.
- [ ] `python test_serial.py` con ID=5 enciende LED verde y suena tono agudo.
- [ ] `python test_serial.py` con ID=0 enciende LED rojo y suena tono grave.
- [ ] `python -m src.tiempo_real` funciona end-to-end con el hardware físico.
- [ ] Al desconectar y reconectar el USB, el sistema se recupera solo.
- [ ] La latencia entre "terminar de hablar" y "encenderse el LED" es < 1.5 segundos.

---

## 8. Problemas comunes específicos de este montaje

| Problema | Causa probable | Solución |
|---|---|---|
| Un LED no enciende | Polaridad invertida | Girar el LED (pata larga al pin, corta a GND). |
| Todos los LEDs encienden a la vez | Cables al GND incorrectos | Verificar que solo los cátodos van a GND, no los ánodos. |
| El LED encendido brilla muy poco | Resistencia demasiado grande | Verificar que es 220Ω, no 2200Ω o 22kΩ. |
| El buzzer no suena con `tone()` | Es un buzzer activo, no pasivo | Usar `digitalWrite(9, HIGH)` en lugar de `tone()`. |
| El Arduino se resetea al enviar tramas | Puede ser fuga eléctrica del buzzer | Añadir una resistencia de 100Ω en serie con el buzzer. |
| El LED amarillo no se usa | El firmware actual no lo enciende explícitamente | Ver "Mejora opcional" abajo. |

---

## 9. Mejora opcional: aprovechar el LED amarillo

En el diseño actual, el LED amarillo (procesando) no se enciende porque el procesamiento en Arduino es prácticamente instantáneo (recibe la trama y actúa). Sin embargo, puedes hacerlo más visible añadiendo una lógica:

**En el firmware, modifica `procesarID`:**

```cpp
void procesarID(byte id) {
  Serial.print("[OK] ID recibido: ");
  Serial.println(id);

  // Efecto "procesando" antes de mostrar resultado
  digitalWrite(PIN_LED_AMARILLO, HIGH);
  delay(300);
  digitalWrite(PIN_LED_AMARILLO, LOW);

  if (id == 0) {
    indicarDesconocido();
  } else {
    indicarReconocido();
  }

  delay(DURACION_DISPLAY_MS);
  apagarLEDs();
}
```

Con esto, cada identificación tiene una secuencia visual: **amarillo (procesando) → verde/rojo (resultado)**. Aporta valor visual en la defensa.

---

## 10. Ajuste opcional al circuito de tu simulación

Comparando tu simulación con esta guía:

- Los **colores de tus LEDs** son correctos (rojo, amarillo, verde).
- El **cableado a GND** parece estar (línea larga verde que va desde el pin GND del Arduino al riel negativo).
- Los **pines** en tu simulación parecen ser D3, D4, D5 (según puedo ver). **Habrá que cambiarlos a D6, D7, D8** o adaptar el firmware.

**Recomendación:** conserva la estructura de tu simulación como referencia y solo mueve los cables al pin correcto según esta guía.

---

## 11. Documentación para la memoria

Anota en `docs/pinout.md` el pinout final:

```markdown
# Pinout del Arduino (versión final)

| Pin | Componente          | Estado                    |
|-----|---------------------|---------------------------|
| D6  | LED verde           | Locutor reconocido        |
| D7  | LED rojo            | Locutor desconocido       |
| D8  | LED amarillo        | Procesando (parpadeo)     |
| D9  | Buzzer              | Tonos según ID            |
| GND | Tierra común        | Riel negativo protoboard  |

**Nota:** el ID del locutor se muestra en la interfaz web, no en displays físicos.
Esta decisión de diseño se justifica en la sección "Arquitectura del sistema"
de la memoria.
```

---

## 12. Próximo paso

Con el hardware validado, la siguiente etapa es el **frontend web** que mostrará el ID del locutor identificado en el navegador. El plan de implementación del frontend se desarrollará en un documento aparte.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
