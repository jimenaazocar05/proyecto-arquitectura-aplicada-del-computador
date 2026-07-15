# ETAPA 5 — Funcionamiento en Tiempo Real

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 5
> **Prerrequisito:** Etapa 4 completada (identificador funcional con precisión ≥ 80%)

---

## 1. Objetivo de la etapa

Construir el módulo de tiempo real que hace del sistema una herramienta viva: en lugar de identificar archivos ya grabados, ahora escucha continuamente por el micrófono, detecta cuándo alguien habla, procesa el fragmento y devuelve el ID en menos de 1 segundo. Esta etapa transforma el proyecto de "script batch" a "sistema interactivo".

Al final de esta etapa, el sistema debe poder:

- Escuchar el micrófono de forma continua sin bloquear el programa.
- Detectar automáticamente cuándo alguien empieza a hablar (VAD).
- Capturar el enunciado completo con una duración razonable.
- Ejecutar el identificador de la Etapa 4 sobre el audio capturado.
- Mostrar el ID resultante en consola con métricas de tiempo.
- Manejar correctamente los silencios, ruidos falsos y ambiente.
- Reiniciar automáticamente para el siguiente enunciado.

---

## 2. Justificación

Esta es la etapa donde el proyecto se convierte en **experiencia demostrable**. Todo lo anterior era necesario pero invisible; esto es lo que verá el tribunal.

**Es el salto de "funcional" a "usable".** El identificador de la Etapa 4 responde a un archivo, pero un usuario real no genera archivos: habla. Esta etapa es el puente entre ambos mundos.

**Introduce problemas nuevos que no existían antes.** El sistema debe lidiar con:
- Silencios prolongados sin procesar audio en vano.
- Ruidos ambientales (portazos, teclado) que no son voz.
- El momento exacto en que empieza y termina un enunciado.
- La latencia percibida: un sistema lento se siente roto.

**Prepara la infraestructura para la Etapa 6.** El bucle principal construido aquí es el mismo que en la Etapa 6 llamará al Arduino. Al terminar la Etapa 5, el módulo de tiempo real está listo para conectarse al hardware.

**Es donde se ejercita el sistema completo en condiciones reales.** Aparecerán casos límite que las pruebas por archivo no revelaron: gente que habla muy bajo, muy rápido, muy cerca del micrófono. Estas observaciones son valiosas para la defensa.

---

## 3. Fundamento teórico

### Voice Activity Detection (VAD)

El VAD decide en cada instante si la señal contiene voz o solo ruido/silencio. El enfoque más simple —y suficiente para este proyecto— se basa en **energía a corto plazo**:

**E(n) = Σ x²[n:n+N]**

donde N es el tamaño de la ventana (típicamente 10-30 ms). Si E(n) supera un umbral, se considera que hay voz.

Para evitar disparos falsos por ruidos breves, se añade una **restricción de duración mínima**: solo se considera "inicio de enunciado" si el nivel se mantiene alto durante al menos ~300 ms.

Análogamente, para el fin del enunciado se exige un **silencio mínimo** de 500-800 ms tras el último frame con voz. Esto tolera pausas naturales del habla.

### Buffer circular y ventana deslizante

Para no perder los primeros milisegundos cuando se detecta el inicio de voz, se mantiene un **buffer circular** de audio de 200-500 ms. Cuando el VAD dispara, se incluye este buffer previo en el fragmento a procesar. De lo contrario, se cortarían las primeras sílabas.

### Latencia percibida vs latencia real

- **Latencia real:** tiempo desde que el usuario habla hasta que el sistema muestra el ID.
- **Latencia percibida:** tiempo desde que el usuario *deja* de hablar hasta que ve el resultado.

La segunda es la que importa. Un sistema que graba 3 segundos y procesa en 0.3 s tiene latencia real de 3.3 s pero latencia percibida de solo 0.3 s. Esta es la métrica objetivo.

---

## 4. Decisiones técnicas previas

Se fijan los parámetros del sistema en tiempo real:

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Modo de captura | **Streaming con callback** | `sounddevice.InputStream` permite audio continuo sin bloqueo. |
| Método VAD | **Energía + duración mínima** | Simple, rápido, sin dependencias extra. Suficiente para entorno de defensa. |
| Umbral de energía | **0.02** (RMS) | Punto de partida. Se calibrará empíricamente. |
| Duración mínima de voz | **300 ms** | Descarta ruidos breves como clicks o portazos. |
| Silencio para fin de enunciado | **700 ms** | Tolera pausas naturales del habla. |
| Buffer circular pre-VAD | **300 ms** | Evita cortar el inicio de la palabra. |
| Duración máxima de enunciado | **5 s** | Corte de seguridad para evitar procesos gigantes. |
| Duración mínima de enunciado | **1 s** | Evita procesar tosidos o palabras muy cortas. |
| Frecuencia de muestreo | **16 000 Hz** | Hereda de `config.py`. |
| Frame de análisis del VAD | **30 ms** | Balance entre resolución temporal y coste. |

---

## 5. Duración estimada

**5 días** de trabajo efectivo (entre 12 y 16 horas en total).

---

## 6. Tareas de la Etapa 5

La etapa se descompone en 7 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 5.1 | Ampliar `config.py` con parámetros de tiempo real | 20 min |
| 5.2 | Implementar el VAD por energía | 2 h |
| 5.3 | Calibrar el umbral de VAD empíricamente | 1.5 h |
| 5.4 | Implementar el detector de enunciados con buffer circular | 3 h |
| 5.5 | Integrar el identificador de la Etapa 4 en el bucle | 2 h |
| 5.6 | Implementar el bucle principal y la salida por consola | 2 h |
| 5.7 | Pruebas de robustez y ajuste fino | 2 h |

---

## 7. Desarrollo de cada tarea

### Tarea 5.1 — Ampliar `config.py` con parámetros de tiempo real

**Qué hacer:** añadir al archivo de configuración los parámetros del VAD y del sistema en tiempo real.

**Añadir al final de `src/config.py`:**

```python
# ============================================================
# TIEMPO REAL Y VAD
# ============================================================
FRAME_VAD_MS = 30                       # Frame de análisis del VAD
UMBRAL_ENERGIA_VAD = 0.02               # Umbral RMS para detectar voz
DURACION_MINIMA_VOZ_MS = 300            # Mínimo de voz para considerarla enunciado
SILENCIO_FIN_ENUNCIADO_MS = 700         # Silencio que marca el fin
DURACION_MAXIMA_ENUNCIADO_S = 5.0       # Corte de seguridad
DURACION_MINIMA_ENUNCIADO_S = 1.0       # Descarta tosidos y palabras sueltas
BUFFER_PREVIO_MS = 300                  # Buffer circular pre-VAD

# Derivados
FRAME_VAD_MUESTRAS = int(FRECUENCIA_MUESTREO * FRAME_VAD_MS / 1000)
```

**Validación de la tarea:** ejecutar `python -c "from src.config import UMBRAL_ENERGIA_VAD; print(UMBRAL_ENERGIA_VAD)"` imprime `0.02`.

---

### Tarea 5.2 — Implementar el VAD por energía

**Qué hacer:** crear un módulo dedicado al VAD que expone una función `es_voz(frame)` para clasificar cada bloque de 30 ms como voz o silencio.

**Crear el archivo `src/vad.py`:**

```python
"""
Módulo de Voice Activity Detection (VAD).
Clasifica frames de audio como voz o silencio basándose en la energía RMS.
"""

import numpy as np

from src.config import UMBRAL_ENERGIA_VAD


def energia_rms(frame: np.ndarray) -> float:
    """
    Calcula la energía RMS (Root Mean Square) de un frame de audio.
    Esta métrica es proporcional al volumen percibido.
    """
    if len(frame) == 0:
        return 0.0
    return float(np.sqrt(np.mean(frame ** 2)))


def es_voz(frame: np.ndarray, umbral: float = None) -> bool:
    """
    Decide si un frame de audio contiene voz o solo silencio/ruido.

    Parámetros
    ----------
    frame : np.ndarray
        Bloque de audio (típicamente 30 ms).
    umbral : float, opcional
        Umbral de energía RMS. Si es None, usa el valor de config.

    Retorna
    -------
    bool
        True si la energía supera el umbral.
    """
    if umbral is None:
        umbral = UMBRAL_ENERGIA_VAD
    return energia_rms(frame) > umbral


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import soundfile as sf
    import sys
    from pathlib import Path

    from src.config import FRAME_VAD_MUESTRAS, FRECUENCIA_MUESTREO

    if len(sys.argv) < 2:
        print("Uso: python -m src.vad <archivo.wav>")
        sys.exit(1)

    audio, fs = sf.read(sys.argv[1])
    if fs != FRECUENCIA_MUESTREO:
        print(f"Advertencia: el archivo tiene {fs} Hz, se esperaban {FRECUENCIA_MUESTREO} Hz.")

    # Analizar el archivo por frames
    num_frames = len(audio) // FRAME_VAD_MUESTRAS
    frames_con_voz = 0
    energias = []

    for i in range(num_frames):
        inicio = i * FRAME_VAD_MUESTRAS
        fin = inicio + FRAME_VAD_MUESTRAS
        frame = audio[inicio:fin]
        e = energia_rms(frame)
        energias.append(e)
        if es_voz(frame):
            frames_con_voz += 1

    porcentaje = (frames_con_voz / num_frames * 100) if num_frames > 0 else 0
    print(f"Archivo:              {Path(sys.argv[1]).name}")
    print(f"Total de frames:      {num_frames}")
    print(f"Frames con voz:       {frames_con_voz} ({porcentaje:.1f}%)")
    print(f"Umbral usado:         {UMBRAL_ENERGIA_VAD}")
    print(f"Energía RMS media:    {np.mean(energias):.4f}")
    print(f"Energía RMS mínima:   {np.min(energias):.4f}")
    print(f"Energía RMS máxima:   {np.max(energias):.4f}")
```

**Ejecutar la prueba:**

```bash
python -m src.vad grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- El script reporta el porcentaje de frames con voz detectada.
- Con una grabación normal (3 seg con habla), debe reportar entre 60% y 90% de frames con voz.
- Con un archivo mayormente silencioso, debe reportar menos del 20%.

---

### Tarea 5.3 — Calibrar el umbral de VAD empíricamente

**Qué hacer:** el umbral por defecto (0.02) es un punto de partida. Puede ser demasiado alto o demasiado bajo según tu micrófono y ambiente. Se calibra empíricamente grabando 5 segundos de silencio y 5 de habla, comparando las energías.

**Crear el archivo `src/calibrar_vad.py`:**

```python
"""
Script de calibración del umbral del VAD.
Graba silencio y habla, y sugiere un umbral empírico.
"""

import numpy as np

from src.audio_capture import grabar
from src.config import FRAME_VAD_MUESTRAS
from src.vad import energia_rms


def calcular_energia_frames(audio: np.ndarray) -> np.ndarray:
    """Devuelve la energía RMS de cada frame de audio."""
    num_frames = len(audio) // FRAME_VAD_MUESTRAS
    energias = np.zeros(num_frames)
    for i in range(num_frames):
        inicio = i * FRAME_VAD_MUESTRAS
        fin = inicio + FRAME_VAD_MUESTRAS
        energias[i] = energia_rms(audio[inicio:fin])
    return energias


def calibrar():
    print("=" * 60)
    print("  CALIBRACIÓN DEL UMBRAL DE VAD")
    print("=" * 60)

    # Fase 1 — Silencio
    print("\nFase 1/2: Grabar SILENCIO durante 5 segundos.")
    print("No hables ni hagas ruido. Solo el ambiente normal de tu habitación.")
    input("Pulsa ENTER cuando estés listo... ")
    silencio = grabar(duracion=5.0)
    energias_silencio = calcular_energia_frames(silencio)

    # Fase 2 — Habla
    print("\nFase 2/2: Grabar HABLA durante 5 segundos.")
    print("Habla con normalidad, como en una conversación. Puedes contar del 1 al 20.")
    input("Pulsa ENTER cuando estés listo... ")
    habla = grabar(duracion=5.0)
    energias_habla = calcular_energia_frames(habla)

    # Análisis
    max_silencio = np.max(energias_silencio)
    p95_silencio = np.percentile(energias_silencio, 95)
    p50_habla = np.median(energias_habla)
    p10_habla = np.percentile(energias_habla, 10)

    print("\n" + "=" * 60)
    print("  RESULTADOS")
    print("=" * 60)
    print(f"Silencio - máximo:         {max_silencio:.4f}")
    print(f"Silencio - percentil 95:   {p95_silencio:.4f}")
    print(f"Habla    - percentil 10:   {p10_habla:.4f}")
    print(f"Habla    - mediana:        {p50_habla:.4f}")

    # Sugerencia de umbral: entre el p95 del silencio y el p10 del habla
    umbral_sugerido = (p95_silencio + p10_habla) / 2
    margen_ok = p10_habla > p95_silencio * 2

    print(f"\nUmbral sugerido:  {umbral_sugerido:.4f}")

    if margen_ok:
        print("El margen entre silencio y habla es amplio. Buen entorno acústico.")
    else:
        print("AVISO: el silencio y el habla tienen energías muy similares.")
        print("       Es posible que haya ruido de fondo alto o que hables muy bajo.")

    print(f"\nActualiza UMBRAL_ENERGIA_VAD en src/config.py con {umbral_sugerido:.4f}")


if __name__ == "__main__":
    calibrar()
```

**Ejecutar la calibración:**

```bash
python -m src.calibrar_vad
```

**Actualizar `config.py` con el valor sugerido.**

**Validación de la tarea:**
- El umbral sugerido está entre el máximo del silencio y el mínimo del habla.
- El sistema reporta "buen entorno acústico" (margen amplio).
- Si el aviso de "energías similares" aparece, revisar el nivel del micrófono en el sistema operativo.

---

### Tarea 5.4 — Implementar el detector de enunciados con buffer circular

**Qué hacer:** el corazón del tiempo real. Un módulo que escucha continuamente y detecta enunciados completos, devolviendo el audio del enunciado listo para procesar.

**Crear el archivo `src/detector_enunciados.py`:**

```python
"""
Detector de enunciados en tiempo real.
Escucha el micrófono continuamente y devuelve fragmentos con voz completa.
"""

import numpy as np
import sounddevice as sd
from collections import deque
from typing import Callable

from src.config import (
    FRECUENCIA_MUESTREO,
    FRAME_VAD_MS,
    FRAME_VAD_MUESTRAS,
    DURACION_MINIMA_VOZ_MS,
    SILENCIO_FIN_ENUNCIADO_MS,
    BUFFER_PREVIO_MS,
    DURACION_MAXIMA_ENUNCIADO_S,
    DURACION_MINIMA_ENUNCIADO_S,
    DISPOSITIVO_ENTRADA,
)
from src.vad import es_voz


class DetectorEnunciados:
    """
    Escucha el micrófono continuamente y detecta enunciados completos.

    Un enunciado se considera:
    - Iniciado: cuando hay ≥ DURACION_MINIMA_VOZ_MS de voz consecutiva.
    - Terminado: cuando hay ≥ SILENCIO_FIN_ENUNCIADO_MS de silencio tras el último frame con voz.

    Al detectar un enunciado completo, llama al callback con el audio.
    """

    def __init__(self, callback: Callable[[np.ndarray], None]):
        self.callback = callback

        # Frames requeridos para las decisiones
        self._frames_min_voz = DURACION_MINIMA_VOZ_MS // FRAME_VAD_MS
        self._frames_silencio_fin = SILENCIO_FIN_ENUNCIADO_MS // FRAME_VAD_MS
        self._frames_buffer_previo = BUFFER_PREVIO_MS // FRAME_VAD_MS
        self._frames_max_enunciado = int(DURACION_MAXIMA_ENUNCIADO_S * 1000) // FRAME_VAD_MS

        # Estado del detector
        self._buffer_previo = deque(maxlen=self._frames_buffer_previo)
        self._enunciado_actual = []
        self._frames_voz_consecutivos = 0
        self._frames_silencio_consecutivos = 0
        self._grabando_enunciado = False

    def _procesar_frame(self, frame: np.ndarray):
        """Procesa un frame nuevo y actualiza el estado del detector."""
        con_voz = es_voz(frame)

        if not self._grabando_enunciado:
            # Estado: esperando inicio de enunciado
            self._buffer_previo.append(frame)

            if con_voz:
                self._frames_voz_consecutivos += 1
                if self._frames_voz_consecutivos >= self._frames_min_voz:
                    # ¡Enunciado iniciado! Incluir buffer previo.
                    self._grabando_enunciado = True
                    self._enunciado_actual = list(self._buffer_previo)
                    self._frames_silencio_consecutivos = 0
            else:
                self._frames_voz_consecutivos = 0

        else:
            # Estado: grabando enunciado
            self._enunciado_actual.append(frame)

            if con_voz:
                self._frames_silencio_consecutivos = 0
            else:
                self._frames_silencio_consecutivos += 1

            # ¿Fin por silencio?
            fin_por_silencio = self._frames_silencio_consecutivos >= self._frames_silencio_fin

            # ¿Fin por duración máxima?
            fin_por_duracion = len(self._enunciado_actual) >= self._frames_max_enunciado

            if fin_por_silencio or fin_por_duracion:
                self._finalizar_enunciado()

    def _finalizar_enunciado(self):
        """Cierra el enunciado actual y llama al callback si es válido."""
        audio_enunciado = np.concatenate(self._enunciado_actual)
        duracion_s = len(audio_enunciado) / FRECUENCIA_MUESTREO

        if duracion_s >= DURACION_MINIMA_ENUNCIADO_S:
            self.callback(audio_enunciado)
        else:
            print(f"  [Descartado: enunciado muy corto ({duracion_s:.2f}s)]")

        # Reset
        self._enunciado_actual = []
        self._frames_voz_consecutivos = 0
        self._frames_silencio_consecutivos = 0
        self._grabando_enunciado = False
        self._buffer_previo.clear()

    def _stream_callback(self, indata, frames, time_info, status):
        """Callback llamado por sounddevice con cada bloque de audio."""
        if status:
            print(f"  [Aviso stream: {status}]")

        # indata tiene shape (frames, canales). Aplanar a mono si es necesario.
        frame = indata[:, 0] if indata.ndim > 1 else indata
        frame = frame.astype(np.float32).flatten()
        self._procesar_frame(frame)

    def escuchar(self):
        """Inicia el bucle de escucha. Bloqueante hasta Ctrl+C."""
        print("Escuchando... (Ctrl+C para detener)")

        with sd.InputStream(
            samplerate=FRECUENCIA_MUESTREO,
            channels=1,
            dtype="float32",
            blocksize=FRAME_VAD_MUESTRAS,
            device=DISPOSITIVO_ENTRADA,
            callback=self._stream_callback,
        ):
            try:
                while True:
                    sd.sleep(100)   # Yield al event loop
            except KeyboardInterrupt:
                print("\nEscucha detenida por el usuario.")


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    """
    Prueba: cada vez que se detecte un enunciado, muestra su duración y RMS.
    """

    def cb(audio):
        duracion = len(audio) / FRECUENCIA_MUESTREO
        rms = float(np.sqrt(np.mean(audio ** 2)))
        print(f"  Enunciado detectado: {duracion:.2f} s, RMS = {rms:.4f}")

    detector = DetectorEnunciados(callback=cb)
    detector.escuchar()
```

**Ejecutar:**

```bash
python -m src.detector_enunciados
```

**Validación de la tarea:**
- Al ejecutarlo, muestra "Escuchando...".
- Cuando hablas, tras dejar de hablar aparece el mensaje de enunciado detectado con su duración.
- Los ruidos breves (chasquidos, teclado) NO disparan detecciones.
- Los silencios prolongados NO generan detecciones.

---

### Tarea 5.5 — Integrar el identificador de la Etapa 4 en el bucle

**Qué hacer:** conectar el detector de enunciados con el `Identificador` de la Etapa 4, adaptando la interfaz para que funcione con arrays de audio en memoria (no solo archivos).

**Modificar `src/identifier.py` para que acepte arrays de audio directamente:**

Añadir al final de la clase `Identificador` (justo antes del bloque `if __name__ == "__main__"`):

```python
    def identificar_audio(self, audio: np.ndarray) -> ResultadoIdentificacion:
        """
        Identifica al locutor a partir de un array de audio en memoria.
        Usa el mismo pipeline que identificar() pero sin pasar por archivo.

        Parámetros
        ----------
        audio : np.ndarray
            Array 1D de audio a la frecuencia de muestreo del proyecto.

        Retorna
        -------
        ResultadoIdentificacion
        """
        from src.preprocesamiento import preprocesar
        from src.feature_extractor import (
            extraer_mfcc_basico, calcular_deltas, normalizar_cmn,
        )
        from src.config import USAR_DELTAS, USAR_DELTA_DELTAS, APLICAR_CMN

        # Pipeline igual al de la Etapa 2, pero sobre array en memoria
        audio_proc = preprocesar(audio)
        mfcc = extraer_mfcc_basico(audio_proc)
        features = mfcc

        if USAR_DELTAS:
            features = np.concatenate([features, calcular_deltas(mfcc)], axis=1)

        if USAR_DELTA_DELTAS:
            from src.feature_extractor import calcular_delta_deltas
            features = np.concatenate([features, calcular_delta_deltas(mfcc)], axis=1)

        if APLICAR_CMN:
            features = normalizar_cmn(features)

        # Reutilizar la lógica existente de scoring y decisión
        scores = self._calcular_scores(features)
        id_mejor = max(scores, key=scores.get)
        llr_max = scores[id_mejor]

        es_desconocido = llr_max < self.umbral
        id_predicho = ID_DESCONOCIDO if es_desconocido else id_mejor

        return ResultadoIdentificacion(
            id_predicho=id_predicho,
            llr_maximo=llr_max,
            id_mejor_candidato=id_mejor,
            scores=scores,
            es_desconocido=es_desconocido,
        )
```

**Validación de la tarea:** ejecutar la siguiente prueba manual en una consola Python:

```python
import soundfile as sf
from src.identifier import Identificador

identificador = Identificador(verbose=True)
audio, _ = sf.read("grabaciones/locutor_01/muestra_001.wav")

# Ambos métodos deben dar el mismo resultado
r1 = identificador.identificar("grabaciones/locutor_01/muestra_001.wav")
r2 = identificador.identificar_audio(audio)

print(f"Archivo:  {r1}")
print(f"Array:    {r2}")
assert r1.id_predicho == r2.id_predicho
print("OK: ambos métodos son consistentes.")
```

---

### Tarea 5.6 — Implementar el bucle principal y la salida por consola

**Qué hacer:** crear el script principal que integra todo: detector + identificador + salida formateada. Este será el "programa demo" hasta que se conecte el Arduino en la Etapa 6.

**Crear el archivo `src/tiempo_real.py`:**

```python
"""
Bucle principal del sistema en tiempo real.
Escucha el micrófono, detecta enunciados, identifica y muestra el resultado.
"""

import time
import numpy as np

from src.detector_enunciados import DetectorEnunciados
from src.identifier import Identificador
from src.config import FRECUENCIA_MUESTREO, ID_DESCONOCIDO


class SistemaTiempoReal:
    """
    Orquesta el sistema completo: detector + identificador.
    """

    def __init__(self):
        print("Cargando identificador y modelos...")
        self.identificador = Identificador(verbose=False)
        self.detector = DetectorEnunciados(callback=self._al_detectar_enunciado)
        self.contador = 0
        print(f"  {len(self.identificador.modelos)} locutores cargados.")
        print(f"  Umbral de decisión: {self.identificador.umbral:.3f}")
        print()

    def _al_detectar_enunciado(self, audio: np.ndarray):
        """Callback llamado cada vez que el detector encuentra un enunciado."""
        self.contador += 1
        duracion = len(audio) / FRECUENCIA_MUESTREO

        # Medir tiempo de procesamiento
        t0 = time.time()
        resultado = self.identificador.identificar_audio(audio)
        t_proceso = time.time() - t0

        # Preparar mensaje
        if resultado.es_desconocido:
            etiqueta = "DESCONOCIDO"
            id_output = 0
            color = "\033[93m"  # Amarillo
        else:
            etiqueta = f"LOCUTOR {resultado.id_predicho:02d}"
            id_output = resultado.id_predicho
            color = "\033[92m"  # Verde

        reset = "\033[0m"

        # Salida en consola
        print(
            f"[Enunciado #{self.contador:03d}] "
            f"duración={duracion:.2f}s | "
            f"procesado en {t_proceso*1000:.0f}ms | "
            f"LLR={resultado.llr_maximo:+.3f}"
        )
        print(f"{color}  →  ID = {id_output:02d}  ({etiqueta}){reset}")
        print()

    def iniciar(self):
        """Arranca el bucle de escucha en tiempo real."""
        print("=" * 60)
        print("  SISTEMA DE IDENTIFICACIÓN DE VOZ EN TIEMPO REAL")
        print("=" * 60)
        print()
        print("Habla al micrófono. El sistema identificará al locutor.")
        print("Pulsa Ctrl+C para detener.")
        print()

        self.detector.escuchar()


if __name__ == "__main__":
    sistema = SistemaTiempoReal()
    sistema.iniciar()
```

**Ejecutar el sistema completo:**

```bash
python -m src.tiempo_real
```

**Validación de la tarea:**
- Al ejecutarlo, muestra el banner de bienvenida.
- Cuando alguien habla, tras un breve procesamiento aparece el ID del locutor en verde (o "DESCONOCIDO" en amarillo).
- El tiempo de procesamiento reportado es inferior a 500 ms.
- La salida sigue funcionando indefinidamente hasta Ctrl+C.

---

### Tarea 5.7 — Pruebas de robustez y ajuste fino

**Qué hacer:** una vez el sistema funciona, hay que probarlo en escenarios reales para detectar casos límite y ajustar parámetros.

**Batería de pruebas manuales:**

**Prueba 1 — Reconocimiento normal:**
- Cada locutor registrado dice «Mi voz es mi clave» tres veces seguidas.
- Verificar que en ≥ 80% de los casos el ID reportado es el correcto.

**Prueba 2 — Rechazo de desconocidos:**
- Una persona no registrada dice varias frases.
- Verificar que la mayoría se marcan como DESCONOCIDO.

**Prueba 3 — Robustez al silencio:**
- Dejar el sistema encendido sin hablar durante 1 minuto.
- Verificar que NO aparecen falsos disparos.

**Prueba 4 — Robustez a ruidos breves:**
- Chasquidos con los dedos, teclado, pequeños golpes.
- Verificar que NO se disparan detecciones (mensaje "descartado: enunciado muy corto").

**Prueba 5 — Enunciado muy largo:**
- Hablar durante más de 5 segundos seguidos.
- Verificar que el sistema procesa un fragmento (por corte de seguridad) y no se cuelga.

**Prueba 6 — Interrupción de una palabra:**
- Empezar a decir la frase y detenerse a mitad, esperar 1 segundo, terminar.
- Observar cómo se comporta (probablemente se procesan como dos enunciados).

**Ajustes finos posibles según los resultados:**

| Síntoma | Ajuste sugerido |
|---|---|
| Se disparan detecciones falsas con ruido ambiente | Subir `UMBRAL_ENERGIA_VAD` |
| No detecta cuando alguien habla bajo | Bajar `UMBRAL_ENERGIA_VAD` |
| Corta las palabras al empezar | Subir `BUFFER_PREVIO_MS` (400-500 ms) |
| Corta antes de que termine la frase | Subir `SILENCIO_FIN_ENUNCIADO_MS` (900-1000 ms) |
| Espera demasiado antes de procesar | Bajar `SILENCIO_FIN_ENUNCIADO_MS` (500 ms) |
| Los ruidos breves se procesan como enunciados | Subir `DURACION_MINIMA_ENUNCIADO_S` (1.5 s) |

**Documentar los ajustes finales aplicados**. Esta documentación va a la memoria como "análisis empírico del sistema en tiempo real".

**Validación final de la etapa:**
- Las 6 pruebas manuales dan resultados aceptables.
- El sistema funciona ininterrumpidamente durante al menos 5 minutos sin fallos.
- La latencia percibida es < 1 segundo en la mayoría de los casos.

---

## 8. Entregables de la Etapa 5

Al finalizar esta etapa se debe contar con:

- Ampliación de `src/config.py` con parámetros de tiempo real.
- Módulo `src/vad.py` con la función VAD por energía.
- Script `src/calibrar_vad.py` para calibración empírica.
- Módulo `src/detector_enunciados.py` con la clase `DetectorEnunciados`.
- Método `identificar_audio()` añadido a la clase `Identificador`.
- Script `src/tiempo_real.py` con el sistema completo.
- Documentación de los ajustes finales aplicados (`docs/ajustes_tiempo_real.md`).
- Vídeo demo (opcional pero muy recomendado) mostrando el sistema en funcionamiento.
- Commit en GitHub con el mensaje "Etapa 5 completada: funcionamiento en tiempo real".

---

## 9. Checklist de validación de la etapa

Antes de pasar a la Etapa 6, verificar:

- [ ] `python -m src.vad <archivo>` reporta porcentajes de voz coherentes.
- [ ] `python -m src.calibrar_vad` produce un umbral empírico razonable.
- [ ] `python -m src.detector_enunciados` detecta enunciados y descarta ruidos breves.
- [ ] `python -m src.tiempo_real` funciona sin errores durante al menos 5 minutos.
- [ ] La latencia de procesamiento es < 500 ms por enunciado.
- [ ] En la prueba de silencio (1 min sin hablar), NO hay falsos disparos.
- [ ] La tasa de identificación correcta en tiempo real es ≥ 70% (será algo menor que en archivo).
- [ ] Los ajustes finales están documentados.
- [ ] Los cambios están subidos al repositorio en GitHub.

---

## 10. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| El sistema no detecta cuando hablo | Umbral VAD demasiado alto | Recalibrar con `calibrar_vad.py`; bajar `UMBRAL_ENERGIA_VAD`. |
| Se dispara con cualquier ruido | Umbral demasiado bajo o duración mínima insuficiente | Subir `UMBRAL_ENERGIA_VAD` o `DURACION_MINIMA_VOZ_MS` (400-500 ms). |
| Corta las primeras palabras | Buffer previo insuficiente | Subir `BUFFER_PREVIO_MS` a 400 o 500 ms. |
| Detecta enunciado varias veces por una sola frase | Silencio de fin demasiado corto: pausas naturales parecen "fin" | Subir `SILENCIO_FIN_ENUNCIADO_MS` a 900-1000 ms. |
| Precisión mucho menor que en archivo | Condiciones acústicas diferentes al entrenamiento | Regrabar muestras de entrenamiento en las mismas condiciones. |
| `PortAudioError` al arrancar | Dispositivo de audio ocupado o cambiado | Cerrar otras aplicaciones que usen el micrófono; reejecutar. |
| Latencia > 1 segundo | Modelos cargándose en cada llamada | Verificar que `Identificador` se instancia UNA vez (fuera del bucle). |
| El programa se cuelga tras varios enunciados | Fuga de memoria acumulando arrays | Verificar que `_enunciado_actual` se resetea tras finalizar. |
| Colores ANSI no se ven en Windows | Terminal antigua sin soporte | Usar Windows Terminal o quitar los códigos `\033[...`. |

---

## 11. Recomendaciones adicionales

**Para la memoria y defensa:**

- Grabar un **vídeo demo** de 30-60 segundos donde se vea a distintas personas hablando y el sistema respondiendo. Es el material audiovisual más impactante para la defensa.
- Incluir en la memoria una **tabla de ajustes finales** con los valores calibrados de todos los parámetros del VAD. Demuestra rigor experimental.
- Documentar la **diferencia de precisión archivo vs tiempo real**: es esperable una caída de 5-15 puntos por el ruido de fondo, la variabilidad de distancia al micrófono, y el corte del VAD. Esto es honestidad científica.

**Para el trabajo posterior (Etapa 6):**

- El callback `_al_detectar_enunciado` es el único punto que hay que modificar para enviar el ID al Arduino. El resto del sistema ya está listo.
- Considerar añadir una cola FIFO entre el detector y el envío al Arduino, por si el hardware es más lento que la detección.

**Consejo de expositor:**

- Pregunta clásica del tribunal: *"¿por qué no usa un VAD basado en aprendizaje profundo como WebRTC VAD o Silero VAD?"*. Respuesta: para un entorno controlado (defensa académica en una sala silenciosa) el VAD por energía es más que suficiente, y su simplicidad lo hace **explicable y determinista**. Un VAD por deep learning añadiría dependencias pesadas, dificultaría el análisis de errores, y no aportaría ganancia real en condiciones controladas. En un despliegue real ruidoso (calle, oficina abierta), sí valdría la pena.

- Otra pregunta típica: *"¿qué latencia tiene el sistema?"*. Respuesta preparada: latencia percibida < 1 segundo, compuesta por: 200 ms de procesamiento MFCC + GMM, más ~700 ms de silencio requerido para cerrar el enunciado. El componente dominante es la espera del fin de enunciado, no el cálculo.

---

## 12. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 6 — Comunicación Serial con el Arduino**, cuyo plan de implementación se desarrollará en un documento aparte.

En la Etapa 6 se sustituirá la salida por consola (`print`) por un envío por puerto serial al microcontrolador, que a su vez mostrará el ID en los displays de 7 segmentos, encenderá los LEDs indicadores y emitirá el sonido correspondiente. Todo el pipeline construido hasta aquí se reutilizará sin modificaciones: solo cambia el callback final.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
