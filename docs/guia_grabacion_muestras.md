# Guía de Grabación de Muestras de Entrenamiento

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Etapa:** 1 — Captura y Almacenamiento de Audio
> **Script utilizado:** `src/grabar_muestras.py`

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Parámetros de grabación](#2-parámetros-de-grabación)
3. [Preparación del entorno físico](#3-preparación-del-entorno-físico)
4. [Cómo usar el script de grabación](#4-cómo-usar-el-script-de-grabación)
5. [Procedimiento por locutor](#5-procedimiento-por-locutor)
6. [Estructura de carpetas resultante](#6-estructura-de-carpetas-resultante)
7. [Validación visual con el visualizador](#7-validación-visual-con-el-visualizador)
8. [Indicadores de calidad](#8-indicadores-de-calidad)
9. [Problemas frecuentes](#9-problemas-frecuentes)
10. [Checklist final](#10-checklist-final)

---

## 1. Requisitos previos

Antes de comenzar, asegúrate de que:

- El entorno virtual está activado:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- El micrófono está conectado y reconocido por el sistema operativo (verificar en *Configuración → Sonido → Entrada*).
- Todos los módulos están instalados (`sounddevice`, `soundfile`, `numpy`).
- Los archivos `src/config.py`, `src/audio_capture.py` y `src/grabar_muestras.py` están presentes.

Para comprobar que el micrófono es detectado correctamente, ejecuta:

```powershell
.\venv\Scripts\python.exe -c "from src.audio_capture import listar_dispositivos; listar_dispositivos()"
```

Busca en la salida el dispositivo con `>` a la izquierda: ese es el micrófono por defecto que usará el sistema.

---

## 2. Parámetros de grabación

Todos los parámetros están centralizados en `src/config.py`. No es necesario modificarlos para la grabación estándar.

| Parámetro | Valor | Descripción |
|---|---|---|
| `FRECUENCIA_MUESTREO` | 16 000 Hz | Estándar en reconocimiento de voz |
| `CANALES` | 1 (mono) | Sin estereofonía, simplifica el procesamiento |
| `PROFUNDIDAD_BITS` | 16 bits | Formato PCM estándar |
| `DURACION_GRABACION` | 3.0 s | Duración fija de cada muestra |
| `MUESTRAS_POR_LOCUTOR` | 10 | Muestras objetivo por cada locutor |

---

## 3. Preparación del entorno físico

Una buena grabación empieza antes de encender el ordenador.

### Condiciones de la sala

- Elegir un lugar con **ruido de fondo moderado o bajo** (una habitación normal es suficiente; no se necesita cabina de grabación).
- Evitar ventiladores directos al micrófono, corrientes de aire y superficies muy reflectantes (cristales, mesas vacías).
- Apagar o silenciar teléfonos móviles durante la sesión.

### Posición del micrófono

- Colocar el micrófono a una distancia de **20–30 cm** de la boca del locutor.
- Mantener esa misma distancia en **todas las tomas** de un mismo locutor.
- Si el micrófono es de solapa (lavalier), pegarlo a la altura del cuello, a unos 10 cm del mentón.
- Evitar que el locutor toque o mueva el micrófono entre grabaciones.

### Nivel del micrófono en Windows

1. Clic derecho en el icono de sonido de la barra de tareas → **Sonidos**.
2. Pestaña **Grabación** → doble clic en el micrófono activo.
3. Pestaña **Niveles** → ajustar a **70–85 %**.
4. Hablar a volumen normal durante 5 segundos y comprobar que el indicador de nivel oscila en la zona media (ni en rojo ni casi invisible).

---

## 4. Cómo usar el script de grabación

Ejecutar siempre desde la **raíz del proyecto**:

```powershell
.\venv\Scripts\python.exe -m src.grabar_muestras
```

### Flujo del script

```
============================================================
  GRABACIÓN DE MUESTRAS DE ENTRENAMIENTO
============================================================

Frase a pronunciar: «Mi voz es mi clave»

Ingresa el ID del locutor (1-20): _
```

1. **Ingresar el ID del locutor** (número entero del 1 al 20).
2. El script muestra cuántas muestras ya existen para ese locutor.
3. Presionar **ENTER** para iniciar la grabación de 3 segundos.
4. Pronunciar la frase inmediatamente después del mensaje `Grabando durante 3.0 segundos...`.
5. Al finalizar, el script muestra la **calidad detectada** y ofrece opciones:

| Tecla | Acción |
|---|---|
| `g` | Guardar la muestra |
| `r` | Reproducir y luego decidir |
| `d` | Descartar la muestra |
| `l` | Listar cuántas muestras lleva el locutor |
| `s` | Salir de la sesión |

---

## 5. Procedimiento por locutor

Repetir el siguiente procedimiento para cada uno de los **3 locutores**.

### Locutor 01 (tú misma / el operador)

```powershell
.\venv\Scripts\python.exe -m src.grabar_muestras
# Ingresar: 1
```

1. Siéntate frente al micrófono en posición cómoda.
2. Pronuncia «**Mi voz es mi clave**» en voz clara y a ritmo natural.
3. Graba **10 muestras** aceptadas (puedes descartar tomas malas sin que cuenten).
4. Introduce pequeñas variaciones naturales entre tomas:
   - Varía ligeramente la velocidad (un poco más rápido, un poco más lento).
   - Varía el tono (más grave, más agudo), pero sin exagerar.
   - No leas mecánicamente; habla como si fuera una frase real de autenticación.
5. Verifica con `l` que acumulas 10 muestras y pulsa `s` para cerrar la sesión.

### Locutor 02 (primer colaborador)

```powershell
.\venv\Scripts\python.exe -m src.grabar_muestras
# Ingresar: 2
```

- El locutor 02 debe ser una **persona diferente** (compañero, familiar, etc.).
- Indica a la persona la posición correcta ante el micrófono y la distancia.
- Muéstrale la frase escrita: **«Mi voz es mi clave»**.
- Deja que se familiarice con la frase pronunciándola una vez de prueba *antes* de iniciar la grabación.
- Graba las 10 muestras siguiendo el mismo protocolo.

### Locutor 03 (segundo colaborador)

```powershell
.\venv\Scripts\python.exe -m src.grabar_muestras
# Ingresar: 3
```

- Mismas instrucciones que el Locutor 02.
- Asegúrate de que el Locutor 03 **no ha escuchado** las tomas del Locutor 02 mientras grababa, para que las variaciones sean independientes.

> **Recomendación de registro:** anota en papel el nombre real de cada locutor y su ID asignado. Esta información es confidencial y no debe subirse al repositorio, pero es útil para la memoria y la defensa.

---

## 6. Estructura de carpetas resultante

Al completar los 3 locutores, la carpeta `grabaciones/` debe tener esta estructura:

```
grabaciones/
├── locutor_01/
│   ├── muestra_001.wav
│   ├── muestra_002.wav
│   ├── muestra_003.wav
│   ├── muestra_004.wav
│   ├── muestra_005.wav
│   ├── muestra_006.wav
│   ├── muestra_007.wav
│   ├── muestra_008.wav
│   ├── muestra_009.wav
│   └── muestra_010.wav
├── locutor_02/
│   └── (misma estructura — 10 archivos)
└── locutor_03/
    └── (misma estructura — 10 archivos)
```

**Total:** 30 archivos `.wav`, cada uno de 3 segundos a 16 kHz mono 16 bits.

Puedes verificar el recuento con:

```powershell
Get-ChildItem -Path .\grabaciones -Recurse -Filter "*.wav" | Measure-Object | Select-Object Count
```

El resultado debe ser **30**.

---

## 7. Validación visual con el visualizador

Tras terminar la grabación, inspecciona al menos **2 muestras de cada locutor** con el visualizador:

```powershell
# Ejemplos de comandos de validación
.\venv\Scripts\python.exe -m src.visualizar_audio grabaciones\locutor_01\muestra_001.wav
.\venv\Scripts\python.exe -m src.visualizar_audio grabaciones\locutor_01\muestra_005.wav
.\venv\Scripts\python.exe -m src.visualizar_audio grabaciones\locutor_02\muestra_003.wav
.\venv\Scripts\python.exe -m src.visualizar_audio grabaciones\locutor_03\muestra_007.wav
```

### Qué buscar en la forma de onda

El visualizador muestra dos líneas de referencia:

| Línea | Color | Significado |
|---|---|---|
| `y = ±0.85` | Roja discontinua | **Umbral de saturación** — los picos NO deben tocarlo |
| `y = ±0.05` | Naranja discontinua | **Umbral de silencio** — la señal debe superar este nivel |

**Forma de onda correcta:**

```
 0.85 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (rojo — no debe tocarse)
      ▁▃▆▇▅▃▁ ▂▅▇▆▄▂▁  ← señal de voz normal
 0.05 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (naranja)
  0   ─────────────────
-0.05 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (naranja)
      ▁▃▆▇▅▃▁ ▂▅▇▆▄▂▁
-0.85 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ (rojo)
```

La señal debe mostrar **actividad visible** (picos claros) en la parte donde se pronunció la frase, y zonas más tranquilas al inicio y al final (silencios naturales de entrada y salida).

---

## 8. Indicadores de calidad

El script muestra automáticamente la calidad tras cada grabación. Esta tabla explica cada nivel:

| Nivel de calidad | Amplitud máxima | Significado | Acción |
|---|---|---|---|
| **Muy baja** | < 0.05 | El micrófono casi no capta nada | Subir ganancia en Windows, acercarse más |
| **Baja** | 0.05 – 0.15 | Señal débil, puede afectar a los MFCC | Hablar más fuerte o acercarse |
| **Correcta** ✅ | 0.15 – 0.85 | Nivel óptimo para el entrenamiento | Guardar |
| **Saturada** | > 0.85 | Clipping — distorsión de la señal | Alejarse del micrófono o bajar ganancia |

El resumen estadístico del visualizador también muestra la **Energía RMS**, que es el indicador más fiable de actividad vocal. Un valor RMS entre **0.05 y 0.30** es ideal.

---

## 9. Problemas frecuentes

### El script no arranca

```
ModuleNotFoundError: No module named 'src'
```

**Solución:** ejecutar siempre desde la **raíz del proyecto**, nunca desde dentro de `src/`.

```powershell
# ❌ Incorrecto
cd src
python grabar_muestras.py

# ✅ Correcto (desde la raíz del proyecto)
.\venv\Scripts\python.exe -m src.grabar_muestras
```

---

### El micrófono no graba nada (amplitud < 0.01)

1. Verificar que el micrófono está seleccionado como dispositivo de entrada por defecto en Windows.
2. Ejecutar `listar_dispositivos()` y anotar el índice del micrófono correcto.
3. Editar `src/config.py` y cambiar:
   ```python
   DISPOSITIVO_ENTRADA = 1   # ← sustituir por el índice correcto
   ```

---

### Grabaciones saturadas de forma sistemática

1. Abrir *Configuración de sonido → Entrada → Propiedades del dispositivo*.
2. Bajar el nivel del micrófono al 60–70 %.
3. Volver a grabar una muestra de prueba y comprobar la amplitud máxima.

---

### El archivo WAV suena distorsionado (metálico)

Puede ocurrir si hay una mezcla de formatos internos. Confirma que `guardar_wav` en `src/audio_capture.py` usa `subtype='PCM_16'`. Si el problema persiste, reinstala `soundfile`:

```powershell
.\venv\Scripts\pip.exe install --upgrade soundfile
```

---

### No hay suficientes muestras en la carpeta

Si el recuento de `.wav` es menor a 10 por locutor, simplemente vuelve a ejecutar el script con el mismo ID de locutor. El numerador automático continuará desde donde quedó:

```powershell
.\venv\Scripts\python.exe -m src.grabar_muestras
# Ingresa el mismo ID — el script te dirá "siguiente muestra será 008" (por ejemplo)
```

---

## 10. Checklist final

Marca cada punto antes de pasar a la Etapa 2:

- [ ] Carpeta `grabaciones/locutor_01/` contiene exactamente 10 archivos `.wav`.
- [ ] Carpeta `grabaciones/locutor_02/` contiene exactamente 10 archivos `.wav`.
- [ ] Carpeta `grabaciones/locutor_03/` contiene exactamente 10 archivos `.wav`.
- [ ] Se han inspeccionado visualmente al menos 2 muestras por locutor con `visualizar_audio`.
- [ ] Ninguna muestra tiene amplitud máxima < 0.05 (silenciosas) ni > 0.90 (saturadas).
- [ ] La duración reportada de cada muestra es **3.00 s**.
- [ ] Los 3 locutores son personas distintas con voces diferentes.
- [ ] Se ha anotado (en papel o documento privado) el nombre real asociado a cada ID.
- [ ] Se ha hecho commit con el mensaje `"Etapa 1 completada: captura y almacenamiento de audio"`.

---

*Documento de la Etapa 1 — Sistema de Identificación de Voces Humanas con Interfaz Física.*
*Asignatura: Arquitectura Aplicada del Computador — UCAB.*
