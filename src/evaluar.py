"""
Evaluación del sistema de identificación.
Recorre el conjunto de prueba y genera la matriz de confusión.
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")   # Backend sin ventana (compatible con cualquier entorno)
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

from src.config import (
    CARPETA_PRUEBAS,
    CARPETA_RESULTADOS,
    UMBRAL_DESCONOCIDO,
    ID_DESCONOCIDO,
    NOMBRE_MATRIZ_CONFUSION_PNG,
    NOMBRE_REPORTE_EVALUACION,
)
from src.identifier import Identificador


def listar_conjuntos_prueba() -> dict:
    """
    Devuelve un diccionario {id_real: [rutas de archivos wav]}.
    ID 0 = desconocidos.
    """
    conjuntos = {}

    if not CARPETA_PRUEBAS.exists():
        return conjuntos

    for carpeta in sorted(CARPETA_PRUEBAS.iterdir()):
        if not carpeta.is_dir():
            continue

        archivos = sorted(carpeta.glob("muestra_*.wav"))
        if not archivos:
            continue

        if carpeta.name == "desconocidos":
            conjuntos[ID_DESCONOCIDO] = archivos
        elif carpeta.name.startswith("locutor_"):
            try:
                id_locutor = int(carpeta.name.split("_")[1])
                conjuntos[id_locutor] = archivos
            except (ValueError, IndexError):
                continue

    return conjuntos


def evaluar(umbral: float = None, guardar_matriz: bool = True, verbose: bool = True):
    """
    Evalúa el sistema sobre el conjunto completo de prueba.

    Retorna un diccionario con:
        - precision_global
        - precision_por_locutor
        - matriz_confusion
        - detalles (lista de predicciones por archivo)
    """
    identificador = Identificador(umbral=umbral, verbose=verbose)
    conjuntos = listar_conjuntos_prueba()

    if not conjuntos:
        print("No hay muestras de prueba. Ejecuta primero `python -m src.grabar_prueba`.")
        return None

    ids_reales_ordenados = sorted(conjuntos.keys())

    # Eje de la matriz: incluye siempre ID=0 (desconocido) para no perder predicciones
    ids_matriz = list(ids_reales_ordenados)
    if ID_DESCONOCIDO not in ids_matriz:
        ids_matriz = [ID_DESCONOCIDO] + ids_matriz
    ids_matriz = sorted(ids_matriz)

    n = len(ids_matriz)
    matriz = np.zeros((n, n), dtype=int)

    detalles = []
    aciertos = 0
    total = 0
    por_locutor = {i: {"aciertos": 0, "total": 0} for i in ids_reales_ordenados}

    for id_real, archivos in conjuntos.items():
        for archivo in archivos:
            resultado = identificador.identificar(archivo)
            id_predicho = resultado.id_predicho

            idx_real = ids_matriz.index(id_real) if id_real in ids_matriz else 0
            idx_pred = ids_matriz.index(id_predicho) if id_predicho in ids_matriz else 0
            matriz[idx_real, idx_pred] += 1
            total += 1
            por_locutor[id_real]["total"] += 1

            correcto = (id_predicho == id_real)
            if correcto:
                aciertos += 1
                por_locutor[id_real]["aciertos"] += 1

            detalles.append({
                "archivo": str(archivo),
                "id_real": id_real,
                "id_predicho": id_predicho,
                "llr_maximo": resultado.llr_maximo,
                "correcto": correcto,
            })

    precision_global = aciertos / total if total > 0 else 0.0
    precision_por_locutor = {
        i: (v["aciertos"] / v["total"] if v["total"] > 0 else 0.0)
        for i, v in por_locutor.items()
    }

    reporte = {
        "timestamp": datetime.now().isoformat(),
        "umbral": identificador.umbral,
        "total_muestras": total,
        "aciertos_totales": aciertos,
        "precision_global": precision_global,
        "precision_por_locutor": {str(k): v for k, v in precision_por_locutor.items()},
        "ids_evaluados": ids_matriz,
        "matriz_confusion": matriz.tolist(),
        "detalles": detalles,
    }

    if verbose:
        _imprimir_resumen(reporte)

    if guardar_matriz:
        _guardar_matriz_confusion(matriz, ids_matriz, precision_global, identificador.umbral)
        _guardar_reporte_json(reporte)

    return reporte


def _imprimir_resumen(reporte: dict):
    print("\n" + "=" * 60)
    print(f"  RESUMEN DE EVALUACIÓN (umbral = {reporte['umbral']:.3f})")
    print("=" * 60)
    print(f"Total de muestras: {reporte['total_muestras']}")
    print(f"Aciertos:          {reporte['aciertos_totales']}")
    print(f"Precisión global:  {reporte['precision_global'] * 100:.2f}%")

    print("\nPrecisión por locutor:")
    for id_locutor, prec in reporte["precision_por_locutor"].items():
        id_int = int(id_locutor)
        etiqueta = "DESCONOCIDO" if id_int == ID_DESCONOCIDO else f"locutor {id_int:02d}"
        print(f"  {etiqueta}: {prec * 100:.2f}%")


def _guardar_matriz_confusion(matriz: np.ndarray, ids: list, precision: float, umbral: float):
    fig, ax = plt.subplots(figsize=(8, 6))

    # Etiquetas legibles
    etiquetas = ["DESC" if i == ID_DESCONOCIDO else f"L{i:02d}" for i in ids]

    img = ax.imshow(matriz, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(ids)))
    ax.set_yticks(range(len(ids)))
    ax.set_xticklabels(etiquetas)
    ax.set_yticklabels(etiquetas)
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    ax.set_title(
        f"Matriz de Confusión\n"
        f"Precisión global: {precision * 100:.2f}% | Umbral: {umbral:.2f}"
    )

    # Escribir el número dentro de cada celda
    for i in range(len(ids)):
        for j in range(len(ids)):
            valor = matriz[i, j]
            color = "white" if valor > matriz.max() / 2 else "black"
            ax.text(j, i, str(valor), ha="center", va="center", color=color, fontweight="bold")

    fig.colorbar(img)
    plt.tight_layout()

    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_RESULTADOS / NOMBRE_MATRIZ_CONFUSION_PNG
    plt.savefig(ruta, dpi=140, bbox_inches="tight")
    plt.close()
    print(f"\nMatriz de confusión guardada en: {ruta}")


def _guardar_reporte_json(reporte: dict):
    ruta = CARPETA_RESULTADOS / NOMBRE_REPORTE_EVALUACION
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"Reporte detallado guardado en: {ruta}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluar el sistema de identificación.")
    parser.add_argument("--umbral", type=float, default=None,
                        help="Umbral de LLR para aceptar identificación.")
    args = parser.parse_args()

    evaluar(umbral=args.umbral)
