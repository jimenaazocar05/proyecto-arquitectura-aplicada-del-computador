"""
Módulo de entrenamiento de modelos GMM.
Provee funciones para entrenar un modelo por locutor.
"""

import time
import numpy as np
from sklearn.mixture import GaussianMixture

from src.config import (
    NUM_COMPONENTES_GMM,
    TIPO_COVARIANZA,
    MAX_ITERACIONES_EM,
    TOLERANCIA_CONVERGENCIA,
    METODO_INICIALIZACION,
    SEMILLA_ALEATORIA,
)


def entrenar_gmm(features: np.ndarray, num_componentes: int = None) -> dict:
    """
    Entrena un modelo GMM sobre una matriz de features.

    Parámetros
    ----------
    features : np.ndarray
        Matriz de shape (n_tramas, n_caracteristicas).
    num_componentes : int, opcional
        Número de componentes gaussianos. Si es None, se usa NUM_COMPONENTES_GMM.

    Retorna
    -------
    dict con las claves:
        - "modelo": el objeto GaussianMixture entrenado.
        - "convergio": bool, si el algoritmo EM alcanzó la convergencia.
        - "iteraciones": int, iteraciones ejecutadas.
        - "log_verosimilitud": float, log-verosimilitud final.
        - "tiempo_s": float, segundos de entrenamiento.
        - "num_muestras_entrenamiento": int, filas de la matriz.
    """
    if num_componentes is None:
        num_componentes = NUM_COMPONENTES_GMM

    # Validaciones
    if features.ndim != 2:
        raise ValueError(f"features debe ser 2D, recibido: {features.shape}")

    if len(features) < num_componentes * 5:
        print(
            f"  [Aviso] Pocas muestras ({len(features)}) para {num_componentes} componentes. "
            "El modelo puede tener baja calidad."
        )

    # Crear el modelo
    gmm = GaussianMixture(
        n_components=num_componentes,
        covariance_type=TIPO_COVARIANZA,
        max_iter=MAX_ITERACIONES_EM,
        tol=TOLERANCIA_CONVERGENCIA,
        init_params=METODO_INICIALIZACION,
        random_state=SEMILLA_ALEATORIA,
        reg_covar=1e-6,   # Regularización para evitar covarianzas singulares
    )

    # Entrenar y medir tiempo
    t0 = time.time()
    gmm.fit(features)
    tiempo = time.time() - t0

    # Log-verosimilitud media por muestra
    log_veros = gmm.score(features)

    return {
        "modelo": gmm,
        "convergio": bool(gmm.converged_),
        "iteraciones": int(gmm.n_iter_),
        "log_verosimilitud": float(log_veros),
        "tiempo_s": float(tiempo),
        "num_muestras_entrenamiento": int(len(features)),
    }


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    from src.dataset import features_de_locutor, listar_locutores

    ids = listar_locutores()
    if not ids:
        print("No hay locutores. Vuelve a la Etapa 1.")
        exit(1)

    id_prueba = ids[0]
    print(f"Entrenando modelo del locutor {id_prueba:02d}...\n")

    features, n = features_de_locutor(id_prueba)
    resultado = entrenar_gmm(features)

    print(f"Muestras usadas:       {n} archivos")
    print(f"Tramas totales:        {resultado['num_muestras_entrenamiento']}")
    print(f"Componentes GMM:       {NUM_COMPONENTES_GMM}")
    print(f"Convergió:             {resultado['convergio']}")
    print(f"Iteraciones EM:        {resultado['iteraciones']}")
    print(f"Log-verosimilitud:     {resultado['log_verosimilitud']:.4f}")
    print(f"Tiempo:                {resultado['tiempo_s']:.2f} s")
