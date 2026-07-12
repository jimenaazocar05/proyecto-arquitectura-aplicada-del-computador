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
