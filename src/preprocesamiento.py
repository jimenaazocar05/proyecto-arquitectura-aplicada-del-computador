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
