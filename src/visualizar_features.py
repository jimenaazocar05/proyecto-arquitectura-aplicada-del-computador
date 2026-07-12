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
    t_orig = np.linspace(0, len(audio) / FRECUENCIA_MUESTREO, len(audio))
    axes[0].plot(t_orig, audio, color="#1F3864", linewidth=0.6)
    axes[0].set_title(f"Forma de onda original — {ruta_wav.name}")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("Amplitud")
    axes[0].grid(True, alpha=0.3)

    # 2. Forma de onda preprocesada
    t_proc = np.linspace(0, len(audio_proc) / FRECUENCIA_MUESTREO, len(audio_proc))
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
    else:
        print("Error: proporciona 1 o 2 archivos WAV como argumentos.")
        sys.exit(1)
