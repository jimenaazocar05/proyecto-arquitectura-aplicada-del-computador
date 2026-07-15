# ETAPA 1 — Captura y Almacenamiento de Audio

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 1
> **Prerrequisito:** Etapa 0 completada (entorno configurado y verificado)

---

## 1. Objetivo de la etapa

Construir un módulo de captura de audio que permita grabar muestras del micrófono con calidad y formato estandarizados, guardarlas en archivos `.wav` correctamente organizados por locutor, y validar que el audio grabado es limpio y utilizable para el entrenamiento posterior de los modelos GMM.

Al final de esta etapa, el sistema debe poder:

- Grabar audio desde el micrófono durante una duración configurable.
- Guardar la grabación en un archivo `.wav` con parámetros estandarizados.
- Organizar automáticamente las grabaciones en carpetas por locutor.
- Visualizar la forma de onda para validar la calidad del audio.

---

## 2. Justificación

La captura de audio parece un paso trivial, pero es donde se originan la mayoría de fallos silenciosos en sistemas de reconocimiento de voz:

**Formato inconsistente entre grabaciones.** Si una grabación se captura a 44.1 kHz en estéreo y otra a 16 kHz en mono, los MFCC extraídos serán incompatibles y el modelo GMM producirá resultados aleatorios.

**Nivel de audio inadecuado.** Grabaciones demasiado bajas se pierden en el ruido de fondo; grabaciones saturadas (clipping) distorsionan las características vocales. Ambos casos degradan la precisión del sistema.

**Ausencia de organización.** Sin una estructura clara de carpetas, entrenar los 20 modelos en la Etapa 3 se vuelve caótico. La convención de nombres se decide ahora, no después.

**Reproducibilidad.** Para poder comparar resultados y depurar, todas las grabaciones deben tener las mismas características técnicas.

---

## 3. Decisiones técnicas previas

Antes de escribir código se fijan los parámetros que se usarán en todo el proyecto. Estos valores se centralizarán en un archivo `config.py`.

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Frecuencia de muestreo | **16 000 Hz** | Estándar en reconocimiento de voz. Suficiente para capturar el rango vocal humano (hasta 8 kHz por Nyquist) y mucho más ligero que 44.1 kHz. |
| Número de canales | **1 (mono)** | La voz no requiere estereofonía. Reduce a la mitad el tamaño de los archivos y simplifica el procesamiento. |
| Profundidad de bits | **16 bits** | Estándar de calidad CD. Formato universalmente soportado por `librosa`, `soundfile` y Windows Media. |
| Duración por grabación | **3 segundos** | Suficiente para pronunciar la frase «mi voz es mi clave» con margen. Balancea información y velocidad de entrenamiento. |
| Formato de archivo | **WAV (PCM)** | Sin compresión, sin pérdida. Es el formato nativo del procesamiento de señales. |
| Modo de captura | **Duración fija** | Simple y suficiente para grabar muestras de entrenamiento. El VAD (detección de voz) llegará en la Etapa 5. |

---

## 4. Duración estimada

**3 días** de trabajo efectivo (entre 8 y 12 horas en total).

---

## 5. Tareas de la Etapa 1

La etapa se descompone en 6 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 1.1 | Crear el módulo de configuración `config.py` | 30 min |
| 1.2 | Implementar la función básica de grabación | 1.5 h |
| 1.3 | Implementar el guardado organizado por locutor | 1 h |
| 1.4 | Crear script interactivo para grabar muestras de entrenamiento | 2 h |
| 1.5 | Implementar visualización de forma de onda | 1.5 h |
| 1.6 | Grabar el conjunto inicial de muestras y validar | 2 h |

---

## 6. Desarrollo de cada tarea

### Tarea 1.1 — Crear el módulo de configuración `config.py`

**Qué hacer:** centralizar en un único archivo todos los parámetros que se usarán en el proyecto. Cambiar un valor aquí se refleja automáticamente en todo el sistema.

**Crear el archivo `src/config.py`:**

```python
"""
Configuración global del proyecto.
Todos los parámetros del sistema se centralizan aquí.
"""

from pathlib import Path

# ============================================================
# RUTAS DEL PROYECTO
# ============================================================
RAIZ = Path(__file__).parent.parent
CARPETA_GRABACIONES = RAIZ / "grabaciones"
CARPETA_MODELOS = RAIZ / "modelos"
CARPETA_PRUEBAS = RAIZ / "pruebas"
CARPETA_RESULTADOS = RAIZ / "resultados"

# ============================================================
# PARÁMETROS DE AUDIO
# ============================================================
FRECUENCIA_MUESTREO = 16000       # Hz
CANALES = 1                        # Mono
PROFUNDIDAD_BITS = 16              # bits
DURACION_GRABACION = 3.0           # segundos

# ============================================================
# LOCUTORES
# ============================================================
NUMERO_MAXIMO_LOCUTORES = 20
MUESTRAS_POR_LOCUTOR = 10          # Se ajusta según pruebas

# ============================================================
# MICRÓFONO
# ============================================================
# None = usar dispositivo por defecto del sistema.
# Cambiar por el índice devuelto por sd.query_devices() si es necesario.
DISPOSITIVO_ENTRADA = None
```

**Validación de la tarea:** ejecutar `python -c "from src.config import FRECUENCIA_MUESTREO; print(FRECUENCIA_MUESTREO)"` desde la raíz del proyecto imprime `16000`.

---

### Tarea 1.2 — Implementar la función básica de grabación

**Qué hacer:** crear la función que captura audio del micrófono durante una duración fija y lo devuelve como un arreglo NumPy listo para guardarse o procesarse.

**Crear el archivo `src/audio_capture.py`:**

```python
"""
Módulo de captura de audio.
Provee las funciones básicas para grabar desde el micrófono.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path

from src.config import (
    FRECUENCIA_MUESTREO,
    CANALES,
    DURACION_GRABACION,
    DISPOSITIVO_ENTRADA,
)


def listar_dispositivos():
    """Muestra todos los dispositivos de audio disponibles."""
    print("=== Dispositivos de audio disponibles ===\n")
    print(sd.query_devices())
    print(f"\nDispositivo por defecto: {sd.default.device}")


def grabar(duracion: float = None) -> np.ndarray:
    """
    Graba audio desde el micrófono durante la duración indicada.

    Parámetros
    ----------
    duracion : float, opcional
        Duración de la grabación en segundos.
        Si es None, usa DURACION_GRABACION de config.py.

    Retorna
    -------
    np.ndarray
        Arreglo con las muestras de audio, shape (N,) para mono.
    """
    if duracion is None:
        duracion = DURACION_GRABACION

    print(f"Grabando durante {duracion} segundos...")

    audio = sd.rec(
        int(duracion * FRECUENCIA_MUESTREO),
        samplerate=FRECUENCIA_MUESTREO,
        channels=CANALES,
        dtype='float32',
        device=DISPOSITIVO_ENTRADA,
    )
    sd.wait()  # Bloquear hasta que termine la grabación

    print("Grabación finalizada.")
    return audio.flatten()  # Convertir de (N, 1) a (N,) para mono


def guardar_wav(audio: np.ndarray, ruta_archivo: Path) -> None:
    """
    Guarda un arreglo de audio en formato WAV.

    Parámetros
    ----------
    audio : np.ndarray
        Arreglo con las muestras de audio.
    ruta_archivo : Path
        Ruta completa del archivo de destino.
    """
    ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
    sf.write(ruta_archivo, audio, FRECUENCIA_MUESTREO, subtype='PCM_16')
    print(f"Archivo guardado: {ruta_archivo}")


def reproducir(audio: np.ndarray) -> None:
    """Reproduce por los altavoces un arreglo de audio."""
    print("Reproduciendo...")
    sd.play(audio, samplerate=FRECUENCIA_MUESTREO)
    sd.wait()
    print("Reproducción finalizada.")


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    listar_dispositivos()
    print("\nSe grabarán 3 segundos. Habla ahora...\n")
    input("Pulsa ENTER para comenzar...")
    audio = grabar()
    print(f"\nMuestras capturadas: {len(audio)}")
    print(f"Duración real: {len(audio) / FRECUENCIA_MUESTREO:.2f} s")
    print(f"Valor máximo: {np.max(np.abs(audio)):.4f}")

    reproducir(audio)

    ruta_prueba = Path(__file__).parent.parent / "grabaciones" / "prueba.wav"
    guardar_wav(audio, ruta_prueba)
```

**Ejecutar la prueba:**

```bash
python -m src.audio_capture
```

**Validación de la tarea:**
- El script lista los dispositivos disponibles.
- Graba 3 segundos y los reproduce.
- Se genera el archivo `grabaciones/prueba.wav`.
- El "valor máximo" mostrado debe estar entre 0.1 y 0.9 (si está cerca de 0, el micrófono no captura; si está cerca de 1, hay saturación).

---

### Tarea 1.3 — Implementar el guardado organizado por locutor

**Qué hacer:** añadir funciones que gestionen automáticamente la estructura de carpetas por locutor y la numeración de las muestras.

**Convención de nombres adoptada:**

```
grabaciones/
├── locutor_01/
│   ├── muestra_001.wav
│   ├── muestra_002.wav
│   └── ...
├── locutor_02/
│   └── ...
```

- El ID del locutor va con dos dígitos (01 a 20).
- El número de muestra va con tres dígitos (001, 002, ...).
- Esto permite ordenación alfabética correcta hasta 999 muestras.

**Añadir al final de `src/audio_capture.py` (antes del bloque `if __name__ == "__main__"`):**

```python
def carpeta_locutor(id_locutor: int) -> Path:
    """
    Devuelve la ruta de la carpeta correspondiente a un locutor.
    Crea la carpeta si no existe.
    """
    from src.config import CARPETA_GRABACIONES

    if not 1 <= id_locutor <= 20:
        raise ValueError(f"ID de locutor debe estar entre 1 y 20, recibido: {id_locutor}")

    carpeta = CARPETA_GRABACIONES / f"locutor_{id_locutor:02d}"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def siguiente_numero_muestra(id_locutor: int) -> int:
    """
    Devuelve el siguiente número de muestra disponible para el locutor.
    Ejemplo: si existen muestra_001.wav y muestra_002.wav, devuelve 3.
    """
    carpeta = carpeta_locutor(id_locutor)
    muestras_existentes = list(carpeta.glob("muestra_*.wav"))
    return len(muestras_existentes) + 1


def guardar_muestra_locutor(audio: np.ndarray, id_locutor: int) -> Path:
    """
    Guarda una grabación en la carpeta correspondiente del locutor,
    con numeración automática.

    Retorna la ruta del archivo creado.
    """
    numero = siguiente_numero_muestra(id_locutor)
    carpeta = carpeta_locutor(id_locutor)
    ruta = carpeta / f"muestra_{numero:03d}.wav"
    guardar_wav(audio, ruta)
    return ruta
```

**Validación de la tarea:** ejecutar en una consola Python:

```python
from src.audio_capture import grabar, guardar_muestra_locutor
audio = grabar()
guardar_muestra_locutor(audio, id_locutor=1)
```

Debe crearse `grabaciones/locutor_01/muestra_001.wav`. Repetir la orden dos veces más y verificar que se crean `muestra_002.wav` y `muestra_003.wav` automáticamente.

---

### Tarea 1.4 — Crear script interactivo para grabar muestras de entrenamiento

**Qué hacer:** un script cómodo que permita al usuario seleccionar el locutor y grabar múltiples muestras seguidas sin tener que escribir código.

**Crear el archivo `src/grabar_muestras.py`:**

```python
"""
Script interactivo para grabar muestras de entrenamiento de un locutor.
Permite grabar varias tomas seguidas y validarlas antes de guardarlas.
"""

import numpy as np
from src.audio_capture import (
    grabar,
    reproducir,
    guardar_muestra_locutor,
    siguiente_numero_muestra,
)
from src.config import MUESTRAS_POR_LOCUTOR


FRASE_ENTRENAMIENTO = "Mi voz es mi clave"


def calidad_grabacion(audio: np.ndarray) -> str:
    """Evalúa cualitativamente la calidad de una grabación."""
    max_amp = np.max(np.abs(audio))
    if max_amp < 0.05:
        return "Muy baja (¿el micrófono captura correctamente?)"
    elif max_amp < 0.15:
        return "Baja (habla más cerca o sube el volumen del micrófono)"
    elif max_amp < 0.85:
        return "Correcta"
    else:
        return "Saturada (posible clipping, aleja el micrófono)"


def main():
    print("=" * 60)
    print("  GRABACIÓN DE MUESTRAS DE ENTRENAMIENTO")
    print("=" * 60)
    print(f"\nFrase a pronunciar: «{FRASE_ENTRENAMIENTO}»\n")

    try:
        id_locutor = int(input("Ingresa el ID del locutor (1-20): "))
    except ValueError:
        print("ID inválido.")
        return

    if not 1 <= id_locutor <= 20:
        print("El ID debe estar entre 1 y 20.")
        return

    numero_inicial = siguiente_numero_muestra(id_locutor)
    print(f"\nLocutor {id_locutor:02d}: siguiente muestra será {numero_inicial:03d}")
    print(f"Objetivo total: {MUESTRAS_POR_LOCUTOR} muestras por locutor.\n")

    while True:
        entrada = input(
            "\n[ENTER] grabar nueva muestra   [s] salir   [l] listar muestras: "
        ).strip().lower()

        if entrada == "s":
            print("Sesión finalizada.")
            break
        elif entrada == "l":
            n = siguiente_numero_muestra(id_locutor) - 1
            print(f"Muestras acumuladas del locutor {id_locutor:02d}: {n}")
            continue

        # Grabar
        print(f"\nPronuncia: «{FRASE_ENTRENAMIENTO}»")
        input("Pulsa ENTER cuando estés listo...")
        audio = grabar()

        # Evaluar calidad
        calidad = calidad_grabacion(audio)
        print(f"Calidad detectada: {calidad}")

        # Ofrecer escucha y decisión
        opcion = input("[g] guardar   [r] reproducir   [d] descartar: ").strip().lower()

        if opcion == "r":
            reproducir(audio)
            opcion = input("[g] guardar   [d] descartar: ").strip().lower()

        if opcion == "g":
            ruta = guardar_muestra_locutor(audio, id_locutor)
            print(f"Guardada: {ruta.name}")
        else:
            print("Muestra descartada.")


if __name__ == "__main__":
    main()
```

**Ejecutar:**

```bash
python -m src.grabar_muestras
```

**Validación de la tarea:** el script permite ingresar el ID de locutor, graba varias muestras, ofrece reproducirlas y guardarlas o descartarlas. Al final, la carpeta del locutor contiene las muestras aceptadas correctamente numeradas.

---

### Tarea 1.5 — Implementar visualización de forma de onda

**Qué hacer:** crear un script que muestre gráficamente la forma de onda de un archivo `.wav`. Esto sirve para verificar visualmente que las grabaciones tienen contenido y no están vacías o saturadas.

**Crear el archivo `src/visualizar_audio.py`:**

```python
"""
Visualización de archivos de audio.
Muestra la forma de onda para inspección visual de las grabaciones.
"""

import sys
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from pathlib import Path


def graficar_forma_onda(ruta_wav: Path) -> None:
    """
    Muestra la forma de onda de un archivo WAV.
    """
    audio, fs = sf.read(ruta_wav)
    tiempo = np.linspace(0, len(audio) / fs, num=len(audio))

    plt.figure(figsize=(12, 4))
    plt.plot(tiempo, audio, linewidth=0.6, color="#1F3864")
    plt.title(f"Forma de onda — {ruta_wav.name}", fontsize=12)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud")
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0.85, color='red', linestyle='--', alpha=0.5, label='Umbral saturación')
    plt.axhline(y=-0.85, color='red', linestyle='--', alpha=0.5)
    plt.axhline(y=0.05, color='orange', linestyle='--', alpha=0.5, label='Umbral silencio')
    plt.axhline(y=-0.05, color='orange', linestyle='--', alpha=0.5)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()


def resumen_estadistico(ruta_wav: Path) -> None:
    """Imprime estadísticas básicas del archivo de audio."""
    audio, fs = sf.read(ruta_wav)
    duracion = len(audio) / fs

    print(f"\nEstadísticas de {ruta_wav.name}:")
    print(f"  Duración         : {duracion:.2f} s")
    print(f"  Frecuencia       : {fs} Hz")
    print(f"  Muestras totales : {len(audio)}")
    print(f"  Amplitud máxima  : {np.max(np.abs(audio)):.4f}")
    print(f"  Amplitud media   : {np.mean(np.abs(audio)):.4f}")
    print(f"  Energía RMS      : {np.sqrt(np.mean(audio**2)):.4f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.visualizar_audio <ruta_al_archivo.wav>")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"El archivo no existe: {ruta}")
        sys.exit(1)

    resumen_estadistico(ruta)
    graficar_forma_onda(ruta)
```

**Ejecutar:**

```bash
python -m src.visualizar_audio grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- Se muestra una ventana con la forma de onda.
- Se imprimen las estadísticas del archivo.
- Las líneas rojas marcan el umbral de saturación (±0.85) y las naranjas el umbral de silencio (±0.05).
- Una grabación correcta debe tener picos entre los umbrales naranja y rojo.

---

### Tarea 1.6 — Grabar el conjunto inicial de muestras y validar

**Qué hacer:** poner en práctica todo lo anterior grabando muestras reales para al menos **3 locutores diferentes**. Esto sirve como validación final de la etapa y prepara el material que se usará en la Etapa 2.

**Procedimiento:**

1. Reclutar a 2 personas más (compañeros, familia) que hagan de locutores 02 y 03. Tú serás el locutor 01.
2. Para cada locutor, ejecutar `python -m src.grabar_muestras` y grabar **10 muestras** de la frase «Mi voz es mi clave».
3. Recomendaciones durante la grabación:
   - Mantener la misma distancia al micrófono en todas las tomas (unos 20-30 cm).
   - Pronunciar la frase con un ritmo natural.
   - Introducir pequeñas variaciones entre tomas (velocidad, tono) para que el modelo generalice mejor.
   - Evitar ruido de fondo intenso, pero no exigir silencio absoluto (mejor entrenar con ruido realista).
4. Al final, ejecutar el visualizador sobre 2-3 muestras aleatorias de cada locutor para verificar visualmente su calidad.

**Validación final de la etapa:** la carpeta `grabaciones/` contiene la siguiente estructura, sin archivos vacíos ni saturados:

```
grabaciones/
├── locutor_01/  (10 archivos muestra_001.wav a muestra_010.wav)
├── locutor_02/  (10 archivos)
└── locutor_03/  (10 archivos)
```

---

## 7. Entregables de la Etapa 1

Al finalizar esta etapa se debe contar con:

- Archivo `src/config.py` con los parámetros globales del proyecto.
- Módulo `src/audio_capture.py` con las funciones de grabación, guardado y reproducción.
- Script `src/grabar_muestras.py` interactivo para grabar muestras por locutor.
- Script `src/visualizar_audio.py` para inspección visual y estadística.
- 30 archivos `.wav` correctamente grabados y organizados (10 por locutor × 3 locutores).
- Commit en GitHub con el mensaje "Etapa 1 completada: captura y almacenamiento de audio".

---

## 8. Checklist de validación de la etapa

Antes de pasar a la Etapa 2, verificar:

- [ ] El archivo `config.py` centraliza correctamente todos los parámetros.
- [ ] `python -m src.audio_capture` graba, reproduce y guarda una prueba sin errores.
- [ ] `python -m src.grabar_muestras` funciona interactivamente y organiza las muestras por carpeta.
- [ ] `python -m src.visualizar_audio <archivo>` muestra la forma de onda y estadísticas.
- [ ] Existen al menos 3 carpetas de locutores con 10 muestras cada una.
- [ ] Al inspeccionar visualmente 5 muestras aleatorias, todas tienen contenido claro (no vacías ni saturadas).
- [ ] La duración real de cada archivo es 3.00 segundos (verificado con el resumen estadístico).
- [ ] Los cambios están subidos al repositorio en GitHub.

---

## 9. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| No se escucha nada al grabar | Micrófono desactivado o dispositivo incorrecto | Ejecutar `listar_dispositivos()` y ajustar `DISPOSITIVO_ENTRADA` en `config.py`. |
| Todas las grabaciones tienen amplitud < 0.05 | Ganancia del micrófono muy baja | Subir el volumen del micrófono en el sistema operativo. |
| Grabaciones saturadas (amplitud = 1.0) | Micrófono demasiado cerca o ganancia excesiva | Alejar el micrófono unos 30 cm o reducir la ganancia. |
| Zumbido de fondo constante | Interferencia eléctrica o micrófono de baja calidad | Cambiar el puerto USB, alejar de fuentes eléctricas. Si es leve, no afecta a MFCC. |
| Error `PortAudioError: Invalid input device` | Índice de dispositivo incorrecto | Volver a `None` en `DISPOSITIVO_ENTRADA` para usar el por defecto. |
| Los archivos WAV se abren con distorsión metálica | Mezcla de dtype (`float32` vs `int16`) | Confirmar que `guardar_wav` usa `subtype='PCM_16'`. |
| `ModuleNotFoundError: No module named 'src'` | Ejecutando desde una carpeta equivocada | Ejecutar siempre desde la raíz del proyecto y usar `python -m src.<modulo>`. |

---

## 10. Recomendaciones adicionales

**Para la memoria y defensa:**

- Guardar una captura de pantalla del visualizador mostrando una forma de onda «buena» y una «mala» (saturada o silenciosa). Es material visual excelente para la memoria.
- Anotar en un cuaderno los ajustes finales del micrófono utilizados (distancia, ganancia). Reproducibilidad.

**Para el trabajo posterior:**

- No borres las muestras aunque parezcan «regulares». La Etapa 2 permitirá comparar visualmente cuáles son mejores y cuáles descartar.
- Empieza a pensar ya en cómo conseguirás grabaciones de más locutores. Idealmente, 10 personas × 10 muestras = 100 archivos para tener un sistema robusto al final.

**Consejo de expositor:**

- El tribunal siempre pregunta: «¿por qué 16 kHz y no 44.1 kHz?». La respuesta correcta está en la tabla de decisiones técnicas (Nyquist + eficiencia). Memorízala.

---

## 11. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 2 — Extracción de Características MFCC**, cuyo plan de implementación se desarrollará en un documento aparte.

En la Etapa 2 se trabajará con los archivos generados aquí para convertir cada `.wav` en su matriz de coeficientes MFCC, que es el «lenguaje» sobre el que operará el clasificador GMM.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
