"""
Módulo de entrada/salida de modelos.
Serializa y carga modelos GMM en formato pickle.
"""

import pickle
from pathlib import Path
from sklearn.mixture import GaussianMixture

from src.config import CARPETA_MODELOS


def ruta_modelo_locutor(id_locutor: int) -> Path:
    """Devuelve la ruta estándar para el modelo de un locutor."""
    return CARPETA_MODELOS / f"locutor_{id_locutor:02d}.pkl"


def ruta_modelo_ubm() -> Path:
    """Devuelve la ruta estándar para el UBM."""
    from src.config import NOMBRE_MODELO_UBM
    return CARPETA_MODELOS / NOMBRE_MODELO_UBM


def guardar_modelo(modelo: GaussianMixture, ruta: Path) -> None:
    """Serializa un modelo GMM a disco en formato pickle."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "wb") as f:
        pickle.dump(modelo, f)


def cargar_modelo(ruta: Path) -> GaussianMixture:
    """Carga un modelo GMM previamente serializado."""
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el modelo en: {ruta}")
    with open(ruta, "rb") as f:
        return pickle.load(f)


def guardar_modelo_locutor(modelo: GaussianMixture, id_locutor: int) -> Path:
    """Guarda el modelo de un locutor con la convención estándar."""
    ruta = ruta_modelo_locutor(id_locutor)
    guardar_modelo(modelo, ruta)
    return ruta


def cargar_modelo_locutor(id_locutor: int) -> GaussianMixture:
    """Carga el modelo de un locutor con la convención estándar."""
    ruta = ruta_modelo_locutor(id_locutor)
    return cargar_modelo(ruta)


def listar_modelos_disponibles() -> list:
    """Devuelve la lista de IDs de locutores con modelo entrenado."""
    if not CARPETA_MODELOS.exists():
        return []

    ids = []
    for archivo in sorted(CARPETA_MODELOS.glob("locutor_*.pkl")):
        try:
            id_locutor = int(archivo.stem.split("_")[1])
            ids.append(id_locutor)
        except (ValueError, IndexError):
            continue
    return ids


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    print("Modelos disponibles:", listar_modelos_disponibles())

    ruta_ubm = ruta_modelo_ubm()
    print(f"Ruta esperada del UBM: {ruta_ubm}")
    print(f"UBM entrenado: {'sí' if ruta_ubm.exists() else 'no'}")
