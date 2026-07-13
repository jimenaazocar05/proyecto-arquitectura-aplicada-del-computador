"""
Calibración del umbral de LLR.
Prueba distintos valores y grafica cómo cambia la precisión del sistema.
"""

import json
import matplotlib
matplotlib.use("Agg")   # Backend sin ventana
import matplotlib.pyplot as plt
from pathlib import Path

from src.config import CARPETA_RESULTADOS, UMBRALES_CALIBRACION
from src.evaluar import evaluar


def calibrar():
    """Evalúa el sistema con un rango de umbrales y genera la curva de precisión."""
    resultados = []

    print("=" * 60)
    print(f"  CALIBRACIÓN DE UMBRAL ({len(UMBRALES_CALIBRACION)} valores)")
    print("=" * 60)

    for umbral in UMBRALES_CALIBRACION:
        print(f"\nProbando umbral = {umbral:.2f} ...", end=" ")
        reporte = evaluar(umbral=umbral, guardar_matriz=False, verbose=False)
        if reporte is None:
            print("Sin muestras de prueba.")
            return

        resultados.append({
            "umbral": umbral,
            "precision_global": reporte["precision_global"],
            "precision_por_locutor": reporte["precision_por_locutor"],
        })
        print(f"Precisión global: {reporte['precision_global'] * 100:.2f}%")

    # Mejor umbral
    mejor = max(resultados, key=lambda r: r["precision_global"])
    print("\n" + "=" * 60)
    print(f"  MEJOR UMBRAL: {mejor['umbral']:.2f} → {mejor['precision_global'] * 100:.2f}%")
    print("=" * 60)
    print(f"\nActualiza UMBRAL_DESCONOCIDO en src/config.py con este valor.")

    # Guardar resultados en JSON
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ruta_json = CARPETA_RESULTADOS / "calibracion_umbral.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"Resultados de calibración guardados en: {ruta_json}")

    # Graficar
    _graficar_curva(resultados, mejor)

    return mejor


def _graficar_curva(resultados: list, mejor: dict):
    umbrales = [r["umbral"] for r in resultados]
    precisiones = [r["precision_global"] * 100 for r in resultados]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(umbrales, precisiones, marker="o", color="#1F3864", linewidth=2)
    ax.axvline(mejor["umbral"], color="red", linestyle="--", alpha=0.5,
               label=f"Óptimo: {mejor['umbral']:.2f}")
    ax.set_xlabel("Umbral de LLR")
    ax.set_ylabel("Precisión global (%)")
    ax.set_title("Calibración del umbral de identificación")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()

    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_RESULTADOS / "curva_calibracion.png"
    plt.savefig(ruta, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"Curva de calibración guardada en: {ruta}")


if __name__ == "__main__":
    calibrar()
