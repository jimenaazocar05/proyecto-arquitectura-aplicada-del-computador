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
