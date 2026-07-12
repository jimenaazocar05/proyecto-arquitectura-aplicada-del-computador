"""
Validación rápida de los modelos entrenados.
Verifica que cada modelo puntúa más alto sus propias muestras que las de otros.
Es un test previo a la construcción del identificador completo (Etapa 4).
"""

import numpy as np
from src.dataset import listar_locutores, features_de_locutor
from src.modelos_io import cargar_modelo_locutor, listar_modelos_disponibles


def puntuar_modelo(modelo, features: np.ndarray) -> float:
    """Devuelve el log-verosimilitud medio por trama."""
    return float(modelo.score(features))


def matriz_de_puntuaciones():
    """
    Genera una matriz cuadrada donde M[i, j] es la puntuación
    del modelo del locutor i evaluado sobre las features del locutor j.

    La diagonal debe tener los valores más altos por columna.
    """
    ids = listar_modelos_disponibles()
    if not ids:
        print("No hay modelos entrenados. Ejecuta primero `python -m src.entrenar_todos`.")
        return None, None

    # Cargar todos los modelos
    modelos = {i: cargar_modelo_locutor(i) for i in ids}

    # Cargar features de cada locutor (validación con datos de entrenamiento)
    features = {i: features_de_locutor(i)[0] for i in ids}

    # Construir matriz
    n = len(ids)
    matriz = np.zeros((n, n))
    for i, id_modelo in enumerate(ids):
        for j, id_features in enumerate(ids):
            matriz[i, j] = puntuar_modelo(modelos[id_modelo], features[id_features])

    return matriz, ids


def imprimir_matriz(matriz: np.ndarray, ids: list) -> None:
    """
    Muestra la matriz de puntuaciones de forma legible en consola.
    Filas = modelos, columnas = features de locutor evaluadas.
    """
    print("\nMatriz de puntuaciones (log-verosimilitud media)")
    print("Filas = modelo | Columnas = features del locutor\n")

    # Cabecera
    print("        ", end="")
    for j in ids:
        print(f"  L{j:02d}   ", end="")
    print()

    # Filas
    aciertos = 0
    for i, id_modelo in enumerate(ids):
        print(f"  L{id_modelo:02d}   ", end="")
        for j in range(len(ids)):
            valor = matriz[i, j]
            # Marcar la diagonal
            if i == j:
                print(f" [{valor:6.2f}]", end="")
            else:
                print(f"  {valor:6.2f} ", end="")
        print()

        # Verificar si el modelo puntúa más alto su propio locutor
        mejor_columna = np.argmax(matriz[i])
        if mejor_columna == i:
            aciertos += 1

    print(f"\nModelos que puntúan mejor su propio locutor: {aciertos}/{len(ids)}")
    if aciertos == len(ids):
        print("VALIDACIÓN CORRECTA: cada modelo reconoce su locutor.")
    else:
        print("AVISO: algunos modelos no discriminan bien. Revisar dataset o parámetros.")


if __name__ == "__main__":
    resultado = matriz_de_puntuaciones()
    if resultado[0] is not None:
        matriz, ids = resultado
        imprimir_matriz(matriz, ids)
