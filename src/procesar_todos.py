"""
Procesa todas las grabaciones existentes y valida el pipeline.
Detecta archivos problemáticos y genera un resumen.
"""

import numpy as np
from pathlib import Path

from src.config import CARPETA_GRABACIONES
from src.feature_extractor import extraer_features


def procesar_todas_las_grabaciones():
    """
    Recorre todas las carpetas de locutores y extrae features
    de cada archivo, reportando errores y estadísticas.
    """
    carpetas_locutores = sorted([
        p for p in CARPETA_GRABACIONES.iterdir()
        if p.is_dir() and p.name.startswith("locutor_")
    ])

    if not carpetas_locutores:
        print("No hay carpetas de locutores en 'grabaciones/'. Vuelve a la Etapa 1.")
        return

    total_archivos = 0
    total_errores = 0
    resumen = []

    for carpeta in carpetas_locutores:
        archivos = sorted(carpeta.glob("muestra_*.wav"))
        print(f"\n--- {carpeta.name} ({len(archivos)} archivos) ---")

        shapes_locutor = []
        errores_locutor = 0

        for archivo in archivos:
            try:
                features = extraer_features(archivo)
                shapes_locutor.append(features.shape)
                total_archivos += 1

                if np.isnan(features).any() or np.isinf(features).any():
                    print(f"  [ERROR] {archivo.name}: contiene NaN o Inf")
                    errores_locutor += 1

            except Exception as e:
                print(f"  [ERROR] {archivo.name}: {e}")
                errores_locutor += 1
                total_errores += 1

        if shapes_locutor:
            frames = [s[0] for s in shapes_locutor]
            print(f"  Tramas por muestra: min={min(frames)}, max={max(frames)}, media={np.mean(frames):.1f}")
            print(f"  Características por trama: {shapes_locutor[0][1]}")
            resumen.append((carpeta.name, len(archivos), errores_locutor))

    print("\n" + "=" * 60)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 60)
    for nombre, total, errores in resumen:
        estado = "OK" if errores == 0 else f"{errores} ERRORES"
        print(f"  {nombre}: {total} archivos — {estado}")
    print(f"\nTotal procesados: {total_archivos}")
    print(f"Total con errores: {total_errores}")


if __name__ == "__main__":
    procesar_todas_las_grabaciones()
