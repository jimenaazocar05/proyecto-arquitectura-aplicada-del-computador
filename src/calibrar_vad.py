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
