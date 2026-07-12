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
