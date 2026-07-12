"""
Módulo de captura de audio.
Provee las funciones básicas para grabar desde el micrófono,
guardar archivos WAV organizados por locutor y reproducir audio.
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
# ORGANIZACIÓN POR LOCUTOR
# ============================================================

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
