"""
Script interactivo para grabar el conjunto de prueba.
Genera muestras nuevas (no usadas en entrenamiento) para evaluar el sistema.
"""

from pathlib import Path

from src.audio_capture import grabar, reproducir, guardar_wav
from src.config import CARPETA_PRUEBAS


def carpeta_prueba_locutor(id_locutor: int) -> Path:
    """Carpeta de pruebas de un locutor registrado (o desconocidos si id=0)."""
    if id_locutor == 0:
        return CARPETA_PRUEBAS / "desconocidos"
    return CARPETA_PRUEBAS / f"locutor_{id_locutor:02d}"


def siguiente_muestra_prueba(id_locutor: int) -> int:
    carpeta = carpeta_prueba_locutor(id_locutor)
    carpeta.mkdir(parents=True, exist_ok=True)
    return len(list(carpeta.glob("muestra_*.wav"))) + 1


def main():
    print("=" * 60)
    print("  GRABACIÓN DE MUESTRAS DE PRUEBA (no usadas en entrenamiento)")
    print("=" * 60)
    print("\nUsa ID 0 para grabar personas DESCONOCIDAS (no registradas).\n")

    try:
        id_locutor = int(input("Ingresa el ID (0=desconocido, 1-20=registrado): "))
    except ValueError:
        print("ID inválido.")
        return

    if not 0 <= id_locutor <= 20:
        print("El ID debe estar entre 0 y 20.")
        return

    carpeta = carpeta_prueba_locutor(id_locutor)
    carpeta.mkdir(parents=True, exist_ok=True)

    n_actual = siguiente_muestra_prueba(id_locutor)
    etiqueta = "DESCONOCIDO" if id_locutor == 0 else f"locutor {id_locutor:02d}"
    print(f"\n{etiqueta}: próxima muestra será la número {n_actual:03d}")
    print(f"Objetivo: al menos 5 muestras.\n")

    while True:
        entrada = input(
            "\n[ENTER] grabar   [s] salir   [l] listar: "
        ).strip().lower()

        if entrada == "s":
            print("Sesión finalizada.")
            break
        elif entrada == "l":
            n = siguiente_muestra_prueba(id_locutor) - 1
            print(f"Muestras de prueba acumuladas: {n}")
            continue

        print("\nPronuncia: «Mi voz es mi clave»")
        input("Pulsa ENTER cuando estés listo...")
        audio = grabar()

        opcion = input("[g] guardar   [r] reproducir   [d] descartar: ").strip().lower()

        if opcion == "r":
            reproducir(audio)
            opcion = input("[g] guardar   [d] descartar: ").strip().lower()

        if opcion == "g":
            n = siguiente_muestra_prueba(id_locutor)
            ruta = carpeta / f"muestra_{n:03d}.wav"
            guardar_wav(audio, ruta)
            print(f"Guardada: {ruta.name}")
        else:
            print("Muestra descartada.")


if __name__ == "__main__":
    main()
