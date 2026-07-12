"""
Módulo de extracción de características MFCC.
Convierte una señal de audio en su matriz de coeficientes MFCC,
incluyendo deltas y normalización CMN.
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


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
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
