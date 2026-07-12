"""
Script principal de entrenamiento.
Entrena los modelos GMM de todos los locutores y el UBM en un solo comando.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from src.config import (
    NUM_COMPONENTES_UBM,
    CARPETA_RESULTADOS,
    NOMBRE_LOG_ENTRENAMIENTO,
)
from src.dataset import (
    listar_locutores,
    features_de_locutor,
    features_de_todos_los_locutores,
)
from src.trainer import entrenar_gmm
from src.modelos_io import (
    guardar_modelo_locutor,
    guardar_modelo,
    ruta_modelo_ubm,
)


def entrenar_todos_los_modelos():
    """
    Entrena los modelos GMM de todos los locutores presentes en la carpeta
    de grabaciones, más el UBM para representar la voz "desconocida".
    """
    ids = listar_locutores()

    if not ids:
        print("No hay locutores registrados. Vuelve a la Etapa 1.")
        return

    print("=" * 60)
    print(f"  ENTRENAMIENTO DE {len(ids)} MODELOS DE LOCUTOR + 1 UBM")
    print("=" * 60)

    log = {
        "timestamp": datetime.now().isoformat(),
        "modelos": {},
        "ubm": {},
    }

    tiempo_total_inicio = time.time()

    # --- Modelos individuales ---
    for id_locutor in ids:
        print(f"\n[Locutor {id_locutor:02d}] Cargando features...", end=" ")
        try:
            features, num_archivos = features_de_locutor(id_locutor)
            print(f"{num_archivos} archivos, {features.shape[0]} tramas.")
        except Exception as e:
            print(f"ERROR: {e}")
            log["modelos"][f"locutor_{id_locutor:02d}"] = {"error": str(e)}
            continue

        print(f"[Locutor {id_locutor:02d}] Entrenando GMM...")
        resultado = entrenar_gmm(features)

        ruta = guardar_modelo_locutor(resultado["modelo"], id_locutor)

        print(
            f"[Locutor {id_locutor:02d}] "
            f"Convergió: {resultado['convergio']} | "
            f"Iter: {resultado['iteraciones']} | "
            f"LogLik: {resultado['log_verosimilitud']:.3f} | "
            f"Tiempo: {resultado['tiempo_s']:.2f}s"
        )
        print(f"[Locutor {id_locutor:02d}] Guardado en: {ruta.name}")

        log["modelos"][f"locutor_{id_locutor:02d}"] = {
            "num_archivos": num_archivos,
            "num_tramas": int(features.shape[0]),
            "convergio": resultado["convergio"],
            "iteraciones": resultado["iteraciones"],
            "log_verosimilitud": resultado["log_verosimilitud"],
            "tiempo_s": resultado["tiempo_s"],
            "ruta": str(ruta),
        }

    # --- UBM (locutor desconocido) ---
    print(f"\n[UBM] Recolectando features de todos los locutores...")
    features_todas = features_de_todos_los_locutores()
    print(f"[UBM] Total de tramas: {features_todas.shape[0]}")

    print(f"[UBM] Entrenando modelo universal con {NUM_COMPONENTES_UBM} componentes...")
    resultado_ubm = entrenar_gmm(features_todas, num_componentes=NUM_COMPONENTES_UBM)

    ruta_ubm = ruta_modelo_ubm()
    guardar_modelo(resultado_ubm["modelo"], ruta_ubm)

    print(
        f"[UBM] Convergió: {resultado_ubm['convergio']} | "
        f"Iter: {resultado_ubm['iteraciones']} | "
        f"LogLik: {resultado_ubm['log_verosimilitud']:.3f} | "
        f"Tiempo: {resultado_ubm['tiempo_s']:.2f}s"
    )
    print(f"[UBM] Guardado en: {ruta_ubm.name}")

    log["ubm"] = {
        "num_tramas": int(features_todas.shape[0]),
        "num_componentes": NUM_COMPONENTES_UBM,
        "convergio": resultado_ubm["convergio"],
        "iteraciones": resultado_ubm["iteraciones"],
        "log_verosimilitud": resultado_ubm["log_verosimilitud"],
        "tiempo_s": resultado_ubm["tiempo_s"],
        "ruta": str(ruta_ubm),
    }

    tiempo_total = time.time() - tiempo_total_inicio
    log["tiempo_total_s"] = tiempo_total

    # Guardar el log en resultados/
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ruta_log = CARPETA_RESULTADOS / NOMBRE_LOG_ENTRENAMIENTO
    with open(ruta_log, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"  ENTRENAMIENTO COMPLETADO EN {tiempo_total:.1f} SEGUNDOS")
    print(f"  Log detallado en: {ruta_log}")
    print("=" * 60)


if __name__ == "__main__":
    entrenar_todos_los_modelos()
