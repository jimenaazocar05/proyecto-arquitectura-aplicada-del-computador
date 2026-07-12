"""
Módulo de gestión del dataset.
Provee funciones para recolectar features desde las carpetas de grabaciones.
"""

import numpy as np
from pathlib import Path
from typing import Tuple

from src.config import CARPETA_GRABACIONES, MIN_MUESTRAS_POR_LOCUTOR
from src.feature_extractor import extraer_features


def listar_locutores() -> list:
    """
    Devuelve la lista de IDs de locutores presentes en la carpeta de grabaciones.
    """
    ids = []
    for carpeta in sorted(CARPETA_GRABACIONES.iterdir()):
        if carpeta.is_dir() and carpeta.name.startswith("locutor_"):
            try:
                id_locutor = int(carpeta.name.split("_")[1])
                ids.append(id_locutor)
            except (ValueError, IndexError):
                continue
    return ids


def carpeta_de_locutor(id_locutor: int) -> Path:
    """Devuelve la ruta de la carpeta correspondiente a un locutor."""
    return CARPETA_GRABACIONES / f"locutor_{id_locutor:02d}"


def features_de_locutor(id_locutor: int) -> Tuple[np.ndarray, int]:
    """
    Extrae y concatena las features de todas las muestras de un locutor.

    Parámetros
    ----------
    id_locutor : int
        Identificador del locutor (1-20).

    Retorna
    -------
    features : np.ndarray
        Matriz de shape (total_tramas, n_caracteristicas).
    num_muestras : int
        Número de archivos procesados.
    """
    carpeta = carpeta_de_locutor(id_locutor)
    archivos = sorted(carpeta.glob("muestra_*.wav"))

    if not archivos:
        raise ValueError(f"No hay grabaciones para el locutor {id_locutor}.")

    if len(archivos) < MIN_MUESTRAS_POR_LOCUTOR:
        raise ValueError(
            f"El locutor {id_locutor} tiene {len(archivos)} muestras, "
            f"se requieren al menos {MIN_MUESTRAS_POR_LOCUTOR}."
        )

    matrices = []
    for archivo in archivos:
        try:
            feats = extraer_features(archivo)
            matrices.append(feats)
        except Exception as e:
            print(f"  [Aviso] No se pudo procesar {archivo.name}: {e}")

    features_consolidadas = np.vstack(matrices)
    return features_consolidadas, len(archivos)


def features_de_todos_los_locutores() -> np.ndarray:
    """
    Concatena las features de todos los locutores disponibles.
    Se usa para entrenar el UBM.
    """
    ids = listar_locutores()
    todas = []

    for id_locutor in ids:
        try:
            feats, _ = features_de_locutor(id_locutor)
            todas.append(feats)
        except Exception as e:
            print(f"  [Aviso] Locutor {id_locutor} omitido: {e}")

    return np.vstack(todas) if todas else np.array([])


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    ids = listar_locutores()
    print(f"Locutores encontrados: {ids}")

    for id_locutor in ids:
        try:
            feats, n = features_de_locutor(id_locutor)
            print(f"Locutor {id_locutor:02d}: {n} muestras -> shape {feats.shape}")
        except Exception as e:
            print(f"Locutor {id_locutor:02d}: ERROR - {e}")
