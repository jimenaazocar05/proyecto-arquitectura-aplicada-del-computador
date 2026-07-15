# ETAPA 2 — Extracción de Características MFCC

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 2
> **Prerrequisito:** Etapa 1 completada (grabaciones de al menos 3 locutores)

---

## 1. Objetivo de la etapa

Construir el módulo de extracción de características que convierte una señal de audio en su representación numérica MFCC, lista para ser usada por el clasificador GMM. Además, generar herramientas de visualización que permitan verificar visualmente que las características capturadas discriminan entre distintos locutores.

Al final de esta etapa, el sistema debe poder:

- Cargar un archivo `.wav` y extraer sus coeficientes MFCC.
- Aplicar preprocesamiento a la señal (normalización, eliminación de silencios).
- Añadir coeficientes delta para capturar dinámica temporal.
- Visualizar la forma de onda, el espectrograma y los MFCC como imagen.
- Comparar visualmente los MFCC de dos locutores diferentes.

---

## 2. Justificación

Los MFCC son el **puente entre la señal de audio y el modelo estadístico**. Todo el sistema depende de que esta transformación funcione correctamente:

**El GMM no ve audio, ve MFCC.** El modelo de la Etapa 3 nunca trabajará con archivos `.wav`; solo con las matrices de coeficientes que produce este módulo. Un error aquí se propaga silenciosamente por todo el sistema.

**Los MFCC deben ser consistentes.** Si en el entrenamiento se extraen con 13 coeficientes y en la identificación con 20, el sistema fallará sin dar error. Por eso los parámetros se fijan en `config.py` una sola vez.

**Los MFCC son la evidencia visual de discriminación.** Si al graficar los MFCC de dos locutores no ves ninguna diferencia visible, el modelo GMM tampoco podrá distinguirlos. Este es un test barato pero muy potente antes de invertir tiempo en entrenamiento.

**Este es el paso "científico" del proyecto.** En la defensa, poder explicar qué es un MFCC, por qué se usa la escala Mel y cómo el DCT decorrelaciona las bandas, es lo que separa un proyecto aprobado de uno sobresaliente.

---

## 3. Fundamento teórico breve

Los **MFCC (Mel-Frequency Cepstral Coefficients)** se calculan en 6 pasos:

1. **Pre-énfasis:** filtro que realza las altas frecuencias, compensando la atenuación natural del habla humana.
2. **Enventanado:** la señal se divide en tramas cortas (típicamente 25 ms) con solape (10 ms). Cada trama se multiplica por una ventana de Hamming para reducir discontinuidades.
3. **FFT:** se calcula el espectro de potencia de cada trama.
4. **Banco de filtros Mel:** el espectro se pasa por un banco de filtros triangulares distribuidos en la escala Mel (percepción humana logarítmica de la frecuencia).
5. **Logaritmo:** se toma el log de la energía en cada filtro, simulando la respuesta logarítmica del oído.
6. **DCT (Transformada Coseno Discreta):** decorrelaciona los coeficientes y compacta la información. Se conservan típicamente los primeros 13.

El resultado es una matriz de forma `(n_frames, n_coeffs)` donde cada fila representa un instante de la señal y cada columna un coeficiente cepstral.

Los **deltas** (Δ) son la derivada temporal de los MFCC: capturan cómo cambian los coeficientes a lo largo del tiempo, información importante para distinguir locutores por su forma de articular.

---

## 4. Decisiones técnicas previas

Se fijan los parámetros de extracción que se usarán en todo el proyecto:

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Número de MFCC | **13** | Estándar clásico. Contiene la información espectral esencial del tracto vocal. |
| Deltas | **Sí (13 adicionales)** | Aportan dinámica temporal. Total de 26 características por trama. |
| Delta-deltas | **No (por ahora)** | Podrían activarse en fase de ajuste fino si la precisión no es suficiente. |
| Longitud de trama | **25 ms** | Estándar en reconocimiento de voz. Suficiente para capturar un fonema. |
| Solape de tramas | **10 ms** | Balance entre resolución temporal y coste computacional. |
| Función de ventana | **Hamming** | Reduce el efecto de discontinuidad en los bordes de la trama. |
| Coeficiente de pre-énfasis | **0.97** | Valor clásico que realza altas frecuencias sin distorsionar. |
| Número de filtros Mel | **26** | Suficiente resolución para el rango de voz humana. |
| Normalización | **CMN (Cepstral Mean Normalization)** | Elimina el sesgo del canal (micrófono, distancia). Crucial. |
| Eliminación de silencios | **Sí (VAD simple por energía)** | Los silencios contaminan los modelos con "no-información". |

---

## 5. Duración estimada

**4 días** de trabajo efectivo (entre 10 y 14 horas en total).

---

## 6. Tareas de la Etapa 2

La etapa se descompone en 6 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 2.1 | Ampliar `config.py` con parámetros MFCC | 30 min |
| 2.2 | Implementar preprocesamiento de audio | 2 h |
| 2.3 | Implementar extracción MFCC básica | 2 h |
| 2.4 | Añadir deltas y normalización CMN | 1.5 h |
| 2.5 | Crear módulo de visualización de características | 2.5 h |
| 2.6 | Procesar el conjunto de grabaciones y validar | 2 h |

---

## 7. Desarrollo de cada tarea

### Tarea 2.1 — Ampliar `config.py` con parámetros MFCC

**Qué hacer:** añadir al archivo de configuración global los parámetros de extracción de características.

**Añadir al final de `src/config.py`:**

```python
# ============================================================
# PARÁMETROS DE EXTRACCIÓN MFCC
# ============================================================
NUM_MFCC = 13                       # Número de coeficientes cepstrales
USAR_DELTAS = True                  # Incluir derivadas de primer orden
USAR_DELTA_DELTAS = False           # Incluir derivadas de segundo orden

LONGITUD_TRAMA_MS = 25              # Longitud de cada trama en milisegundos
SOLAPE_TRAMA_MS = 10                # Solape entre tramas en milisegundos

# Derivados (se calculan a partir de FRECUENCIA_MUESTREO)
LONGITUD_TRAMA_MUESTRAS = int(FRECUENCIA_MUESTREO * LONGITUD_TRAMA_MS / 1000)
SOLAPE_TRAMA_MUESTRAS = int(FRECUENCIA_MUESTREO * SOLAPE_TRAMA_MS / 1000)

# Parámetros del banco de filtros
NUM_FILTROS_MEL = 26                # Número de filtros triangulares Mel
COEF_PREENFASIS = 0.97              # Coeficiente del filtro de pre-énfasis

# ============================================================
# PREPROCESAMIENTO
# ============================================================
APLICAR_CMN = True                  # Cepstral Mean Normalization
APLICAR_VAD = True                  # Voice Activity Detection simple
UMBRAL_VAD_DB = -35                 # Umbral en dB para detectar silencio
```

**Validación de la tarea:** ejecutar `python -c "from src.config import NUM_MFCC; print(NUM_MFCC)"` desde la raíz imprime `13`.

---

### Tarea 2.2 — Implementar preprocesamiento de audio

**Qué hacer:** crear las funciones que preparan la señal antes de extraer los MFCC. Incluye normalización de amplitud, pre-énfasis y eliminación de silencios.

**Crear el archivo `src/preprocesamiento.py`:**

```python
"""
Módulo de preprocesamiento de audio.
Prepara la señal antes de la extracción de características MFCC.
"""

import numpy as np
import librosa

from src.config import (
    FRECUENCIA_MUESTREO,
    COEF_PREENFASIS,
    UMBRAL_VAD_DB,
    APLICAR_VAD,
)


def normalizar_amplitud(audio: np.ndarray) -> np.ndarray:
    """
    Escala la señal para que su amplitud máxima sea 1.0.
    Compensa diferencias de volumen entre grabaciones.
    """
    max_abs = np.max(np.abs(audio))
    if max_abs < 1e-6:
        return audio
    return audio / max_abs


def preenfasis(audio: np.ndarray, coef: float = None) -> np.ndarray:
    """
    Aplica el filtro de pre-énfasis: y[n] = x[n] - coef * x[n-1].
    Realza las altas frecuencias, importantes para la inteligibilidad del habla.
    """
    if coef is None:
        coef = COEF_PREENFASIS
    return np.append(audio[0], audio[1:] - coef * audio[:-1])


def eliminar_silencios(audio: np.ndarray, umbral_db: float = None) -> np.ndarray:
    """
    Elimina fragmentos de silencio de la señal.
    Un VAD simple basado en energía: descarta tramas por debajo del umbral.

    Nota: librosa.effects.trim solo elimina silencio inicial/final.
    Para VAD interno más agresivo, se usa split.
    """
    if umbral_db is None:
        umbral_db = UMBRAL_VAD_DB

    # Detecta segmentos no silenciosos
    segmentos = librosa.effects.split(audio, top_db=abs(umbral_db))

    if len(segmentos) == 0:
        return audio  # Si no detecta nada, devuelve original

    # Concatena solo las partes con voz
    audio_sin_silencio = np.concatenate([audio[inicio:fin] for inicio, fin in segmentos])
    return audio_sin_silencio


def preprocesar(audio: np.ndarray) -> np.ndarray:
    """
    Pipeline completo de preprocesamiento.
    Aplica en orden: normalización, VAD, pre-énfasis.
    """
    audio = normalizar_amplitud(audio)

    if APLICAR_VAD:
        audio = eliminar_silencios(audio)

    audio = preenfasis(audio)
    return audio


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import soundfile as sf
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Uso: python -m src.preprocesamiento <archivo.wav>")
        sys.exit(1)

    audio, fs = sf.read(sys.argv[1])
    print(f"Audio original: {len(audio)} muestras, {len(audio)/fs:.2f} s")

    audio_proc = preprocesar(audio)
    print(f"Audio procesado: {len(audio_proc)} muestras, {len(audio_proc)/fs:.2f} s")
    print(f"Amplitud máxima: {np.max(np.abs(audio_proc)):.4f}")
```

**Ejecutar la prueba:**

```bash
python -m src.preprocesamiento grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- La duración procesada es menor o igual que la original (por la eliminación de silencios).
- La amplitud máxima está normalizada (cercana a 1.0).
- No hay errores en la ejecución.

---

### Tarea 2.3 — Implementar extracción MFCC básica

**Qué hacer:** crear el módulo principal de extracción de características, que combina el preprocesamiento con la llamada a librosa para obtener los MFCC.

**Crear el archivo `src/feature_extractor.py`:**

```python
"""
Módulo de extracción de características MFCC.
Convierte una señal de audio en su matriz de coeficientes MFCC.
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path

from src.config import (
    FRECUENCIA_MUESTREO,
    NUM_MFCC,
    NUM_FILTROS_MEL,
    LONGITUD_TRAMA_MUESTRAS,
    SOLAPE_TRAMA_MUESTRAS,
    USAR_DELTAS,
    USAR_DELTA_DELTAS,
    APLICAR_CMN,
)
from src.preprocesamiento import preprocesar


def extraer_mfcc_basico(audio: np.ndarray) -> np.ndarray:
    """
    Extrae los coeficientes MFCC básicos de una señal.

    Parámetros
    ----------
    audio : np.ndarray
        Señal de audio ya preprocesada.

    Retorna
    -------
    np.ndarray
        Matriz de shape (n_frames, NUM_MFCC).
    """
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=FRECUENCIA_MUESTREO,
        n_mfcc=NUM_MFCC,
        n_fft=LONGITUD_TRAMA_MUESTRAS,
        hop_length=SOLAPE_TRAMA_MUESTRAS,
        n_mels=NUM_FILTROS_MEL,
    )
    # librosa devuelve shape (n_mfcc, n_frames). Trasponemos para (n_frames, n_mfcc).
    return mfcc.T


def cargar_audio(ruta_wav: Path) -> np.ndarray:
    """Carga un archivo WAV a la frecuencia de muestreo del proyecto."""
    audio, fs = sf.read(str(ruta_wav))

    # Verificar frecuencia de muestreo
    if fs != FRECUENCIA_MUESTREO:
        # Resamplear si es necesario (defensivo)
        audio = librosa.resample(audio, orig_sr=fs, target_sr=FRECUENCIA_MUESTREO)

    # Si el audio es estéreo, convertirlo a mono
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    return audio.astype(np.float32)


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m src.feature_extractor <archivo.wav>")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    audio = cargar_audio(ruta)
    audio_proc = preprocesar(audio)
    mfcc = extraer_mfcc_basico(audio_proc)

    print(f"Archivo: {ruta.name}")
    print(f"Duración procesada: {len(audio_proc) / FRECUENCIA_MUESTREO:.2f} s")
    print(f"Shape de MFCC: {mfcc.shape}")
    print(f"  {mfcc.shape[0]} tramas × {mfcc.shape[1]} coeficientes")
    print(f"Valor medio: {mfcc.mean():.4f}")
    print(f"Desviación : {mfcc.std():.4f}")
```

**Ejecutar la prueba:**

```bash
python -m src.feature_extractor grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- Se imprime la forma de la matriz MFCC (aproximadamente 300 tramas × 13 coeficientes para 3 segundos).
- Los valores medios y desviaciones no son NaN ni infinitos.

---

### Tarea 2.4 — Añadir deltas y normalización CMN

**Qué hacer:** ampliar el extractor para incluir las derivadas temporales (deltas) y la normalización CMN, que son clave para mejorar la discriminación entre locutores.

**Añadir al final de `src/feature_extractor.py` (antes del bloque `if __name__`):**

```python
def calcular_deltas(mfcc: np.ndarray) -> np.ndarray:
    """
    Calcula las derivadas de primer orden (deltas) de los MFCC.
    Se traspone porque librosa opera sobre el eje temporal.
    """
    deltas = librosa.feature.delta(mfcc.T, order=1).T
    return deltas


def calcular_delta_deltas(mfcc: np.ndarray) -> np.ndarray:
    """
    Calcula las derivadas de segundo orden (delta-deltas) de los MFCC.
    """
    delta2 = librosa.feature.delta(mfcc.T, order=2).T
    return delta2


def normalizar_cmn(features: np.ndarray) -> np.ndarray:
    """
    Cepstral Mean Normalization: resta la media de cada coeficiente
    a lo largo del tiempo. Elimina el efecto del canal (micrófono, distancia).

    Parámetros
    ----------
    features : np.ndarray
        Matriz de features de shape (n_frames, n_coefs).

    Retorna
    -------
    np.ndarray
        Matriz normalizada del mismo shape.
    """
    return features - np.mean(features, axis=0, keepdims=True)


def extraer_features(ruta_wav: Path) -> np.ndarray:
    """
    Pipeline completo de extracción de características.
    Aplica preprocesamiento, MFCC, deltas opcionales y CMN.

    Retorna
    -------
    np.ndarray
        Matriz de características de shape (n_frames, n_coefs_totales).
        n_coefs_totales = NUM_MFCC * (1 + USAR_DELTAS + USAR_DELTA_DELTAS)
    """
    # 1. Cargar y preprocesar audio
    audio = cargar_audio(ruta_wav)
    audio = preprocesar(audio)

    # 2. Extraer MFCC básicos
    mfcc = extraer_mfcc_basico(audio)
    features = mfcc

    # 3. Añadir deltas si está configurado
    if USAR_DELTAS:
        deltas = calcular_deltas(mfcc)
        features = np.concatenate([features, deltas], axis=1)

    # 4. Añadir delta-deltas si está configurado
    if USAR_DELTA_DELTAS:
        delta2 = calcular_delta_deltas(mfcc)
        features = np.concatenate([features, delta2], axis=1)

    # 5. Normalización CMN
    if APLICAR_CMN:
        features = normalizar_cmn(features)

    return features
```

**Reemplazar el bloque `if __name__ == "__main__"` por:**

```python
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m src.feature_extractor <archivo.wav>")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    features = extraer_features(ruta)

    print(f"Archivo: {ruta.name}")
    print(f"Shape final: {features.shape}")
    print(f"  {features.shape[0]} tramas × {features.shape[1]} características")
    print(f"Valor medio (tras CMN): {features.mean():.4f} (debería estar cerca de 0)")
    print(f"Desviación: {features.std():.4f}")
```

**Ejecutar:**

```bash
python -m src.feature_extractor grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- La matriz final tiene 26 características por trama (13 MFCC + 13 deltas).
- El valor medio tras CMN es prácticamente 0 (menor a 0.01 en valor absoluto).
- No hay NaN ni infinitos.

---

### Tarea 2.5 — Crear módulo de visualización de características

**Qué hacer:** construir herramientas visuales para inspeccionar el resultado del pipeline. Estas visualizaciones son oro para la memoria y la defensa.

**Crear el archivo `src/visualizar_features.py`:**

```python
"""
Visualización de características de audio.
Genera gráficos para inspeccionar formas de onda, espectrogramas y MFCC.
"""

import sys
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path

from src.config import (
    FRECUENCIA_MUESTREO,
    LONGITUD_TRAMA_MUESTRAS,
    SOLAPE_TRAMA_MUESTRAS,
    CARPETA_RESULTADOS,
)
from src.feature_extractor import cargar_audio, extraer_features, extraer_mfcc_basico
from src.preprocesamiento import preprocesar


def graficar_completo(ruta_wav: Path, guardar: bool = False) -> None:
    """
    Muestra un panel con 4 gráficos:
    1. Forma de onda original
    2. Forma de onda preprocesada
    3. Espectrograma
    4. MFCC (heatmap)
    """
    audio = cargar_audio(ruta_wav)
    audio_proc = preprocesar(audio)
    mfcc = extraer_mfcc_basico(audio_proc)

    fig, axes = plt.subplots(4, 1, figsize=(12, 10))

    # 1. Forma de onda original
    t_orig = np.linspace(0, len(audio)/FRECUENCIA_MUESTREO, len(audio))
    axes[0].plot(t_orig, audio, color="#1F3864", linewidth=0.6)
    axes[0].set_title(f"Forma de onda original — {ruta_wav.name}")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("Amplitud")
    axes[0].grid(True, alpha=0.3)

    # 2. Forma de onda preprocesada
    t_proc = np.linspace(0, len(audio_proc)/FRECUENCIA_MUESTREO, len(audio_proc))
    axes[1].plot(t_proc, audio_proc, color="#0F6E56", linewidth=0.6)
    axes[1].set_title("Forma de onda preprocesada (normalizada, sin silencios, con pre-énfasis)")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_ylabel("Amplitud")
    axes[1].grid(True, alpha=0.3)

    # 3. Espectrograma
    espectrograma = np.abs(librosa.stft(
        audio_proc,
        n_fft=LONGITUD_TRAMA_MUESTRAS,
        hop_length=SOLAPE_TRAMA_MUESTRAS
    ))
    espectrograma_db = librosa.amplitude_to_db(espectrograma, ref=np.max)
    img_esp = librosa.display.specshow(
        espectrograma_db,
        sr=FRECUENCIA_MUESTREO,
        hop_length=SOLAPE_TRAMA_MUESTRAS,
        x_axis="time",
        y_axis="hz",
        ax=axes[2],
        cmap="magma",
    )
    axes[2].set_title("Espectrograma (dB)")
    fig.colorbar(img_esp, ax=axes[2], format="%+2.0f dB")

    # 4. MFCC
    img_mfcc = librosa.display.specshow(
        mfcc.T,
        sr=FRECUENCIA_MUESTREO,
        hop_length=SOLAPE_TRAMA_MUESTRAS,
        x_axis="time",
        ax=axes[3],
        cmap="viridis",
    )
    axes[3].set_title("Coeficientes MFCC (13 coeficientes)")
    axes[3].set_ylabel("Coeficiente")
    fig.colorbar(img_mfcc, ax=axes[3])

    plt.tight_layout()

    if guardar:
        CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
        ruta_salida = CARPETA_RESULTADOS / f"features_{ruta_wav.stem}.png"
        plt.savefig(ruta_salida, dpi=120, bbox_inches="tight")
        print(f"Gráfico guardado en: {ruta_salida}")

    plt.show()


def comparar_locutores(ruta_wav_1: Path, ruta_wav_2: Path, guardar: bool = False) -> None:
    """
    Compara visualmente los MFCC de dos archivos de audio.
    Útil para verificar que el pipeline discrimina entre locutores diferentes.
    """
    feat1 = extraer_features(ruta_wav_1)
    feat2 = extraer_features(ruta_wav_2)

    fig, axes = plt.subplots(2, 1, figsize=(12, 6))

    img1 = axes[0].imshow(feat1.T, aspect="auto", origin="lower", cmap="viridis")
    axes[0].set_title(f"Features de {ruta_wav_1.parent.name} / {ruta_wav_1.name}")
    axes[0].set_ylabel("Coeficiente")
    fig.colorbar(img1, ax=axes[0])

    img2 = axes[1].imshow(feat2.T, aspect="auto", origin="lower", cmap="viridis")
    axes[1].set_title(f"Features de {ruta_wav_2.parent.name} / {ruta_wav_2.name}")
    axes[1].set_xlabel("Trama")
    axes[1].set_ylabel("Coeficiente")
    fig.colorbar(img2, ax=axes[1])

    plt.tight_layout()

    if guardar:
        CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
        ruta_salida = CARPETA_RESULTADOS / f"comparacion_{ruta_wav_1.parent.name}_vs_{ruta_wav_2.parent.name}.png"
        plt.savefig(ruta_salida, dpi=120, bbox_inches="tight")
        print(f"Comparación guardada en: {ruta_salida}")

    plt.show()


# ============================================================
# INTERFAZ DE LÍNEA DE COMANDOS
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  Un archivo:      python -m src.visualizar_features <archivo.wav>")
        print("  Comparar dos:    python -m src.visualizar_features <archivo1.wav> <archivo2.wav>")
        print("  Guardar imagen:  añadir --guardar al final")
        sys.exit(1)

    guardar = "--guardar" in sys.argv
    argumentos = [a for a in sys.argv[1:] if a != "--guardar"]

    if len(argumentos) == 1:
        graficar_completo(Path(argumentos[0]), guardar=guardar)
    elif len(argumentos) == 2:
        comparar_locutores(Path(argumentos[0]), Path(argumentos[1]), guardar=guardar)
```

**Ejecutar las visualizaciones:**

```bash
# Gráfico completo de una muestra
python -m src.visualizar_features grabaciones/locutor_01/muestra_001.wav --guardar

# Comparar dos locutores diferentes
python -m src.visualizar_features grabaciones/locutor_01/muestra_001.wav grabaciones/locutor_02/muestra_001.wav --guardar
```

**Validación de la tarea:**
- Se muestran los cuatro paneles: forma de onda original, procesada, espectrograma y MFCC.
- Al comparar dos locutores, los patrones de colores en los MFCC son visiblemente distintos.
- Las imágenes se guardan correctamente en `resultados/`.

---

### Tarea 2.6 — Procesar el conjunto de grabaciones y validar

**Qué hacer:** ejecutar el pipeline sobre todas las grabaciones acumuladas hasta ahora, verificar que ningún archivo falla, y generar comparaciones visuales entre los 3 locutores para incluirlas en la memoria.

**Crear el archivo `src/procesar_todos.py`:**

```python
"""
Procesa todas las grabaciones existentes y valida el pipeline.
Detecta archivos problemáticos y genera un resumen.
"""

import numpy as np
from pathlib import Path

from src.config import CARPETA_GRABACIONES
from src.feature_extractor import extraer_features


def procesar_todas_las_grabaciones():
    """
    Recorre todas las carpetas de locutores y extrae features
    de cada archivo, reportando errores y estadísticas.
    """
    carpetas_locutores = sorted([
        p for p in CARPETA_GRABACIONES.iterdir()
        if p.is_dir() and p.name.startswith("locutor_")
    ])

    if not carpetas_locutores:
        print("No hay carpetas de locutores en 'grabaciones/'. Vuelve a la Etapa 1.")
        return

    total_archivos = 0
    total_errores = 0
    resumen = []

    for carpeta in carpetas_locutores:
        archivos = sorted(carpeta.glob("muestra_*.wav"))
        print(f"\n--- {carpeta.name} ({len(archivos)} archivos) ---")

        shapes_locutor = []
        errores_locutor = 0

        for archivo in archivos:
            try:
                features = extraer_features(archivo)
                shapes_locutor.append(features.shape)
                total_archivos += 1

                if np.isnan(features).any() or np.isinf(features).any():
                    print(f"  [ERROR] {archivo.name}: contiene NaN o Inf")
                    errores_locutor += 1

            except Exception as e:
                print(f"  [ERROR] {archivo.name}: {e}")
                errores_locutor += 1
                total_errores += 1

        if shapes_locutor:
            frames = [s[0] for s in shapes_locutor]
            print(f"  Tramas por muestra: min={min(frames)}, max={max(frames)}, media={np.mean(frames):.1f}")
            print(f"  Características por trama: {shapes_locutor[0][1]}")
            resumen.append((carpeta.name, len(archivos), errores_locutor))

    print("\n" + "=" * 60)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 60)
    for nombre, total, errores in resumen:
        estado = "OK" if errores == 0 else f"{errores} ERRORES"
        print(f"  {nombre}: {total} archivos — {estado}")
    print(f"\nTotal procesados: {total_archivos}")
    print(f"Total con errores: {total_errores}")


if __name__ == "__main__":
    procesar_todas_las_grabaciones()
```

**Ejecutar:**

```bash
python -m src.procesar_todos
```

**Generar las comparaciones visuales para la memoria:**

```bash
python -m src.visualizar_features grabaciones/locutor_01/muestra_001.wav grabaciones/locutor_02/muestra_001.wav --guardar
python -m src.visualizar_features grabaciones/locutor_01/muestra_001.wav grabaciones/locutor_03/muestra_001.wav --guardar
python -m src.visualizar_features grabaciones/locutor_02/muestra_001.wav grabaciones/locutor_03/muestra_001.wav --guardar
```

**Validación final de la etapa:**
- El script `procesar_todos.py` reporta 0 errores en todas las carpetas.
- El número de tramas por muestra es consistente (todas alrededor del mismo valor).
- La carpeta `resultados/` contiene al menos 3 imágenes de comparación entre locutores.
- Al inspeccionar las imágenes, los MFCC de locutores distintos muestran patrones visualmente diferentes.

---

## 8. Entregables de la Etapa 2

Al finalizar esta etapa se debe contar con:

- Ampliación de `src/config.py` con parámetros MFCC.
- Módulo `src/preprocesamiento.py` con normalización, VAD y pre-énfasis.
- Módulo `src/feature_extractor.py` con extracción MFCC + deltas + CMN.
- Módulo `src/visualizar_features.py` con visualización completa y comparativa.
- Script `src/procesar_todos.py` que valida el pipeline sobre todo el dataset.
- Al menos 3 imágenes de comparación entre locutores guardadas en `resultados/`.
- Commit en GitHub con el mensaje "Etapa 2 completada: extracción de características MFCC".

---

## 9. Checklist de validación de la etapa

Antes de pasar a la Etapa 3, verificar:

- [ ] Ejecutar `python -m src.feature_extractor grabaciones/locutor_01/muestra_001.wav` devuelve una matriz de shape `(N, 26)`.
- [ ] El valor medio tras CMN es prácticamente 0.
- [ ] `python -m src.visualizar_features <archivo>` muestra los cuatro paneles correctamente.
- [ ] `python -m src.procesar_todos` reporta 0 errores sobre las 30 grabaciones iniciales.
- [ ] Las comparaciones visuales entre locutores muestran patrones MFCC visiblemente distintos.
- [ ] Ningún archivo produce NaN, Inf ni errores.
- [ ] Los cambios están subidos al repositorio en GitHub.

---

## 10. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| Matriz MFCC con NaN o Inf | Grabación silenciosa (VAD eliminó todo) | Ajustar `UMBRAL_VAD_DB` a un valor más permisivo (-40 dB) o desactivar VAD. |
| Todas las muestras tienen shape distinta | Variabilidad de duración tras VAD | Es normal y no afecta al GMM, que trabaja con tramas independientes. |
| Los MFCC de locutores distintos se ven iguales | CMN eliminó demasiada información, o el audio es muy corto | Verificar que las grabaciones tienen contenido claro; probar sin CMN temporalmente. |
| `librosa.effects.split` devuelve arreglo vacío | Umbral VAD demasiado estricto | Bajar `UMBRAL_VAD_DB` a -40 o -45 dB. |
| Error `n_fft too large for input signal` | Audio más corto que la ventana FFT | Grabaciones muy cortas (< 25 ms). Verificar en Etapa 1. |
| Los deltas son todo ceros | Menos de 9 tramas (librosa requiere mínimo para derivar) | La grabación es demasiado corta; ampliar duración en Etapa 1. |
| El gráfico se congela en Windows | Backend de matplotlib mal configurado | Usar `matplotlib.use("TkAgg")` al inicio del script. |

---

## 11. Recomendaciones adicionales

**Para la memoria y defensa:**

- Guarda las imágenes de comparación entre locutores en `resultados/`. Son las **piezas visuales más potentes** de toda la memoria: demuestran que el sistema puede discriminar antes incluso de entrenar el clasificador.
- Prepara una diapositiva con los 6 pasos del cálculo del MFCC (pre-énfasis, enventanado, FFT, filtros Mel, log, DCT). Los tribunales adoran esta pregunta.
- Ten claro por qué se usa la **escala Mel** (percepción logarítmica del oído humano) y por qué el **DCT decorrelaciona** los coeficientes.

**Para el trabajo posterior:**

- Si al comparar visualmente dos locutores los MFCC se ven casi idénticos, el sistema tendrá muchas dificultades para distinguirlos. Considera regrabar con más contraste (voz masculina vs femenina, por ejemplo, para las primeras pruebas).
- El pipeline debe ser **determinista**: el mismo archivo procesado dos veces debe dar exactamente los mismos MFCC. Añade una prueba manual para verificarlo.

**Consejo de expositor:**

- Pregunta clásica del tribunal: «¿Por qué no usa el espectrograma directamente en lugar de MFCC?». Respuesta: el espectrograma tiene demasiadas dimensiones correlacionadas; los MFCC compactan la información en 13 valores independientes gracias al DCT, y son perceptualmente relevantes gracias a la escala Mel.

---

## 12. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 3 — Entrenamiento de Modelos GMM por Locutor**, cuyo plan de implementación se desarrollará en un documento aparte.

En la Etapa 3 se usarán las funciones de extracción construidas aquí para entrenar un modelo GMM por cada locutor, produciendo los archivos `.pkl` que el sistema cargará para identificar voces en la Etapa 4.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
