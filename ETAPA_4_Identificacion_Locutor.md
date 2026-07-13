# ETAPA 4 — Identificación de Locutor a partir de Archivo

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 4
> **Prerrequisito:** Etapa 3 completada (modelos GMM + UBM entrenados y validados)

---

## 1. Objetivo de la etapa

Construir el módulo de identificación que, dado un archivo de audio nuevo, decida a cuál de los locutores registrados pertenece (o si es desconocido). Esta es la primera etapa donde el sistema **decide algo**, y su resultado se traduce en el ID (0-20) que en la Etapa 6 se enviará al Arduino.

Al final de esta etapa, el sistema debe poder:

- Cargar todos los modelos entrenados (locutores + UBM) una sola vez en memoria.
- Puntuar una nueva grabación contra todos los modelos usando LLR.
- Decidir el locutor más probable o marcar como desconocido (ID = 0).
- Reportar la confianza de la decisión.
- Evaluar el sistema completo sobre un conjunto de prueba y generar la **matriz de confusión**.
- Calibrar el umbral de "desconocido" con datos reales.

---

## 2. Justificación

Esta etapa es el **momento de la verdad** del proyecto:

**Aquí se mide el sistema.** Los resultados de la Etapa 3 (matriz de puntuaciones) son un indicio; los de la Etapa 4 son la **medida oficial de precisión**. La matriz de confusión generada aquí es el gráfico más importante para la defensa.

**El umbral de "desconocido" es un problema clásico de biometría.** Sin un umbral bien calibrado, el sistema comete uno de dos errores:
- Umbral demasiado bajo → cualquier voz se identifica como algún registrado (falsos positivos).
- Umbral demasiado alto → ni siquiera reconoce a los propios locutores registrados (falsos negativos).

El equilibrio se busca empíricamente, y eso es exactamente lo que se hará en esta etapa.

**La separación entrenamiento/prueba es innegociable.** Evaluar el sistema con los mismos datos con los que se entrenó daría precisiones artificialmente altas. En esta etapa se grabarán **muestras de prueba nuevas**, que el modelo nunca ha visto, para obtener una estimación honesta de la precisión.

**Esta etapa produce el módulo que la Etapa 5 (tiempo real) llamará miles de veces.** El identificador debe ser rápido: <500 ms por muestra. Esto se logra cargando los modelos una sola vez y reutilizándolos.

---

## 3. Fundamento teórico breve

### Log-Likelihood Ratio (LLR)

Dado un vector de features **X** y un modelo GMM del locutor **i** (modelo Mᵢ), la log-verosimilitud es:

**LL(X, Mᵢ) = log P(X | Mᵢ)**

En biometría de voz, se prefiere el **Log-Likelihood Ratio** normalizado por el UBM:

**LLR(X, Mᵢ) = log P(X | Mᵢ) - log P(X | UBM)**

Esta cantidad responde a la pregunta: *"¿cuánto más probable es que la voz X provenga del locutor i, en comparación con la voz humana genérica?"*

- **LLR positivo:** la muestra se parece más al locutor i que a la voz genérica → probable coincidencia.
- **LLR cercano a 0:** la muestra se parece tanto al locutor i como a cualquier otra voz humana → probable desconocido.
- **LLR negativo:** la muestra se parece más a la voz genérica que al locutor i → probable rechazo.

### Regla de decisión

1. Calcular LLR(X, Mᵢ) para todos los locutores registrados.
2. Elegir el locutor con LLR máximo como candidato ganador.
3. Si el LLR del ganador supera el umbral T → asignar su ID.
4. Si no → asignar ID = 0 (desconocido).

### Matriz de confusión

Es una tabla donde las filas representan el locutor **real** y las columnas el locutor **predicho**. La diagonal contiene los aciertos; los valores fuera de la diagonal son los errores. Es el resumen visual estándar del rendimiento de cualquier clasificador.

---

## 4. Decisiones técnicas previas

Se fijan los parámetros del identificador:

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Método de puntuación | **LLR (score - UBM)** | Estándar en biometría de voz. Compensa el efecto del canal. |
| Umbral inicial | **0.5** | Punto de partida conservador. Se calibrará empíricamente. |
| Detección de desconocido | **Umbral absoluto sobre LLR máximo** | Simple, interpretable, defendible. |
| Muestras de prueba por locutor | **3-5 (nuevas)** | Suficiente para una matriz de confusión estable. NO deben estar en entrenamiento. |
| Muestras de desconocidos | **3-5 personas nunca registradas** | Para calibrar el umbral. |
| Almacenamiento en memoria | **Diccionario id → modelo** | Carga única al arrancar; latencia mínima por identificación. |
| Formato de la matriz de confusión | **PNG + JSON** | Imagen para memoria, JSON para trazabilidad. |

---

## 5. Duración estimada

**5 días** de trabajo efectivo (entre 12 y 16 horas en total).

---

## 6. Tareas de la Etapa 4

La etapa se descompone en 7 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 4.1 | Ampliar `config.py` con parámetros del identificador | 20 min |
| 4.2 | Implementar la carga en memoria de todos los modelos | 1 h |
| 4.3 | Implementar la función de puntuación LLR | 1.5 h |
| 4.4 | Implementar la función `identificar()` con umbral | 2 h |
| 4.5 | Grabar el conjunto de prueba (muestras nuevas + desconocidos) | 2 h |
| 4.6 | Implementar la evaluación y matriz de confusión | 3 h |
| 4.7 | Calibrar el umbral de desconocido | 2 h |

---

## 7. Desarrollo de cada tarea

### Tarea 4.1 — Ampliar `config.py` con parámetros del identificador

**Qué hacer:** añadir al archivo de configuración los parámetros del identificador y la calibración del umbral.

**Añadir al final de `src/config.py`:**

```python
# ============================================================
# PARÁMETROS DEL IDENTIFICADOR
# ============================================================
USAR_LLR = True                     # True: LLR (score - UBM). False: LL directo.
UMBRAL_DESCONOCIDO = 0.5            # LLR mínimo para aceptar identificación
ID_DESCONOCIDO = 0                  # ID reservado para locutor desconocido

# ============================================================
# EVALUACIÓN
# ============================================================
NOMBRE_MATRIZ_CONFUSION_PNG = "matriz_confusion.png"
NOMBRE_REPORTE_EVALUACION = "reporte_evaluacion.json"

# Rango de umbrales a probar durante la calibración
UMBRALES_CALIBRACION = [i * 0.1 for i in range(-10, 21)]   # -1.0 a 2.0 en pasos de 0.1
```

**Validación de la tarea:** ejecutar `python -c "from src.config import UMBRAL_DESCONOCIDO; print(UMBRAL_DESCONOCIDO)"` imprime `0.5`.

---

### Tarea 4.2 — Implementar la carga en memoria de todos los modelos

**Qué hacer:** crear una clase o función que cargue una sola vez los modelos entrenados y el UBM, y los mantenga en memoria para identificaciones rápidas.

**Crear el archivo `src/identifier.py`:**

```python
"""
Módulo de identificación de locutores.
Carga los modelos entrenados y decide a quién pertenece una nueva grabación.
"""

import numpy as np
from pathlib import Path
from dataclasses import dataclass

from src.config import (
    UMBRAL_DESCONOCIDO,
    ID_DESCONOCIDO,
    USAR_LLR,
)
from src.feature_extractor import extraer_features
from src.modelos_io import (
    cargar_modelo_locutor,
    cargar_modelo,
    ruta_modelo_ubm,
    listar_modelos_disponibles,
)


@dataclass
class ResultadoIdentificacion:
    """Estructura que empaqueta el resultado de una identificación."""
    id_predicho: int          # 0 si desconocido, 1-20 si registrado
    llr_maximo: float          # LLR del mejor candidato
    id_mejor_candidato: int    # ID del mejor candidato aunque no supere el umbral
    scores: dict               # {id_locutor: llr}
    es_desconocido: bool

    def __repr__(self):
        etiqueta = "DESCONOCIDO" if self.es_desconocido else f"locutor {self.id_predicho:02d}"
        return (
            f"ResultadoIdentificacion({etiqueta}, "
            f"llr_max={self.llr_maximo:.3f}, "
            f"mejor_candidato={self.id_mejor_candidato:02d})"
        )


class Identificador:
    """
    Identificador de locutor.
    Carga los modelos una sola vez y expone la función identificar().
    """

    def __init__(self, umbral: float = None, verbose: bool = False):
        self.umbral = umbral if umbral is not None else UMBRAL_DESCONOCIDO
        self.verbose = verbose
        self.modelos = {}
        self.ubm = None
        self._cargar_todos()

    def _cargar_todos(self):
        """Carga en memoria los modelos de todos los locutores registrados y el UBM."""
        ids = listar_modelos_disponibles()
        if not ids:
            raise RuntimeError(
                "No hay modelos entrenados. Ejecuta primero `python -m src.entrenar_todos`."
            )

        for id_locutor in ids:
            self.modelos[id_locutor] = cargar_modelo_locutor(id_locutor)

        # Cargar UBM si existe
        ruta_ubm = ruta_modelo_ubm()
        if ruta_ubm.exists():
            self.ubm = cargar_modelo(ruta_ubm)
        elif USAR_LLR:
            raise RuntimeError(
                "USAR_LLR=True requiere UBM entrenado. "
                "Ejecuta `python -m src.entrenar_todos`."
            )

        if self.verbose:
            print(f"Identificador cargado: {len(self.modelos)} locutores + "
                  f"{'UBM' if self.ubm else 'sin UBM'}")

    def _calcular_scores(self, features: np.ndarray) -> dict:
        """
        Calcula el score de cada modelo sobre las features dadas.
        Si USAR_LLR está activo, aplica normalización por UBM.
        """
        scores = {}

        if USAR_LLR and self.ubm is not None:
            score_ubm = self.ubm.score(features)
            for id_locutor, modelo in self.modelos.items():
                scores[id_locutor] = modelo.score(features) - score_ubm
        else:
            for id_locutor, modelo in self.modelos.items():
                scores[id_locutor] = modelo.score(features)

        return scores

    def identificar(self, ruta_wav: Path) -> ResultadoIdentificacion:
        """
        Identifica al locutor de una grabación.

        Parámetros
        ----------
        ruta_wav : Path
            Ruta al archivo WAV a identificar.

        Retorna
        -------
        ResultadoIdentificacion
        """
        features = extraer_features(Path(ruta_wav))
        scores = self._calcular_scores(features)

        # Ganador
        id_mejor = max(scores, key=scores.get)
        llr_max = scores[id_mejor]

        # Decisión final según umbral
        es_desconocido = llr_max < self.umbral
        id_predicho = ID_DESCONOCIDO if es_desconocido else id_mejor

        return ResultadoIdentificacion(
            id_predicho=id_predicho,
            llr_maximo=llr_max,
            id_mejor_candidato=id_mejor,
            scores=scores,
            es_desconocido=es_desconocido,
        )
```

**Validación de la tarea:** el archivo se importa sin errores. Todavía no se prueba: eso será en la siguiente tarea.

---

### Tarea 4.3 — Implementar la función de puntuación LLR

**Nota:** la función `_calcular_scores` ya está incluida en la clase de la tarea anterior. Aquí solo se verifica su correcto funcionamiento.

**Añadir al final de `src/identifier.py` (dentro del archivo, fuera de la clase):**

```python
# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m src.identifier <archivo.wav>")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"El archivo no existe: {ruta}")
        sys.exit(1)

    identificador = Identificador(verbose=True)
    print(f"\nIdentificando: {ruta.name}\n")

    resultado = identificador.identificar(ruta)

    print("--- SCORES POR LOCUTOR (LLR) ---")
    for id_locutor, score in sorted(resultado.scores.items(), key=lambda x: -x[1]):
        marca = " ← ganador" if id_locutor == resultado.id_mejor_candidato else ""
        print(f"  Locutor {id_locutor:02d}: {score:+.3f}{marca}")

    print(f"\nUmbral configurado: {identificador.umbral:.3f}")
    print(f"LLR del ganador: {resultado.llr_maximo:.3f}")

    if resultado.es_desconocido:
        print(f"\n*** DECISIÓN: LOCUTOR DESCONOCIDO (ID = 0) ***")
        print(f"    Mejor candidato habría sido: locutor {resultado.id_mejor_candidato:02d}")
    else:
        print(f"\n*** DECISIÓN: LOCUTOR {resultado.id_predicho:02d} ***")
```

**Ejecutar la prueba:**

```bash
# Probar con una muestra de entrenamiento (debe reconocerla correctamente)
python -m src.identifier grabaciones/locutor_01/muestra_001.wav
```

**Validación de la tarea:**
- El script identifica correctamente el locutor 01.
- El LLR del ganador es notablemente superior al de los demás.
- El programa reporta también los scores de los otros locutores para trazabilidad.

---

### Tarea 4.4 — Implementar la función `identificar()` con umbral

**Nota:** la lógica del umbral ya está integrada en el método `identificar()` de la clase. Aquí solo se hace una prueba adicional con un umbral configurable desde la línea de comandos, útil para experimentar sin tocar `config.py`.

**Ampliar `src/identifier.py` para aceptar el umbral desde CLI:**

Reemplazar el bloque `if __name__ == "__main__"` por:

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Identificar locutor de un archivo WAV.")
    parser.add_argument("archivo", type=str, help="Ruta al archivo WAV.")
    parser.add_argument("--umbral", type=float, default=None,
                        help="Umbral de LLR para aceptar identificación.")
    args = parser.parse_args()

    ruta = Path(args.archivo)
    if not ruta.exists():
        print(f"El archivo no existe: {ruta}")
        sys.exit(1)

    identificador = Identificador(umbral=args.umbral, verbose=True)
    print(f"\nIdentificando: {ruta.name}\n")

    resultado = identificador.identificar(ruta)

    print("--- SCORES POR LOCUTOR (LLR) ---")
    for id_locutor, score in sorted(resultado.scores.items(), key=lambda x: -x[1]):
        marca = " ← ganador" if id_locutor == resultado.id_mejor_candidato else ""
        print(f"  Locutor {id_locutor:02d}: {score:+.3f}{marca}")

    print(f"\nUmbral configurado: {identificador.umbral:.3f}")
    print(f"LLR del ganador: {resultado.llr_maximo:.3f}")

    if resultado.es_desconocido:
        print(f"\n*** DECISIÓN: LOCUTOR DESCONOCIDO (ID = 0) ***")
        print(f"    Mejor candidato habría sido: locutor {resultado.id_mejor_candidato:02d}")
    else:
        print(f"\n*** DECISIÓN: LOCUTOR {resultado.id_predicho:02d} ***")
```

Añadir al inicio del archivo:

```python
import sys
```

**Ejecutar prueba con umbrales variados:**

```bash
python -m src.identifier grabaciones/locutor_01/muestra_001.wav --umbral 0.5
python -m src.identifier grabaciones/locutor_01/muestra_001.wav --umbral 5.0
python -m src.identifier grabaciones/locutor_01/muestra_001.wav --umbral -5.0
```

**Validación de la tarea:**
- Con umbral 0.5 y 5.0: reconoce correctamente al locutor 01 (asumiendo que el LLR es alto).
- Con umbral 50 (imposible): reporta desconocido.
- Con umbral -5.0: reconoce siempre al locutor con LLR más alto.

---

### Tarea 4.5 — Grabar el conjunto de prueba

**Qué hacer:** grabar un conjunto de muestras completamente nuevas (que NO se usaron para entrenar), tanto de los locutores registrados como de personas desconocidas. Esto es indispensable para una evaluación honesta.

**Crear el script `src/grabar_prueba.py`:**

```python
"""
Script interactivo para grabar el conjunto de prueba.
Genera muestras nuevas (no usadas en entrenamiento) para evaluar el sistema.
"""

from pathlib import Path

from src.audio_capture import grabar, reproducir, guardar_wav, siguiente_numero_muestra
from src.config import CARPETA_PRUEBAS


def carpeta_prueba_locutor(id_locutor: int) -> Path:
    """Carpeta de pruebas de un locutor registrado."""
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
```

**Ejecutar y grabar:**

Grabar 5 muestras nuevas por cada locutor registrado y 5 muestras de al menos 2 personas desconocidas:

```bash
python -m src.grabar_prueba   # Ingresar ID 1, grabar 5
python -m src.grabar_prueba   # Ingresar ID 2, grabar 5
python -m src.grabar_prueba   # Ingresar ID 3, grabar 5
python -m src.grabar_prueba   # Ingresar ID 0, grabar 5-10 de personas desconocidas
```

**Estructura resultante:**

```
pruebas/
├── locutor_01/     (5 muestras nuevas)
├── locutor_02/     (5 muestras nuevas)
├── locutor_03/     (5 muestras nuevas)
└── desconocidos/   (5-10 muestras de personas no registradas)
```

**Validación de la tarea:** la carpeta `pruebas/` contiene la estructura esperada, con archivos nuevos que NO están en `grabaciones/`.

---

### Tarea 4.6 — Implementar la evaluación y matriz de confusión

**Qué hacer:** crear el módulo que evalúa el sistema sobre el conjunto de prueba, calcula la precisión global y por locutor, y genera la matriz de confusión como imagen PNG.

**Crear el archivo `src/evaluar.py`:**

```python
"""
Evaluación del sistema de identificación.
Recorre el conjunto de prueba y genera la matriz de confusión.
"""

import json
import numpy as np
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
    n = len(ids_reales_ordenados)
    matriz = np.zeros((n, n), dtype=int)

    detalles = []
    aciertos = 0
    total = 0
    por_locutor = {i: {"aciertos": 0, "total": 0} for i in ids_reales_ordenados}

    for id_real, archivos in conjuntos.items():
        idx_real = ids_reales_ordenados.index(id_real)

        for archivo in archivos:
            resultado = identificador.identificar(archivo)
            id_predicho = resultado.id_predicho

            # Índice de la columna correspondiente en la matriz
            if id_predicho in ids_reales_ordenados:
                idx_pred = ids_reales_ordenados.index(id_predicho)
            else:
                # Si el modelo predice un locutor cuyo ID no está en el eje de pruebas,
                # lo tratamos como desconocido para la matriz
                idx_pred = ids_reales_ordenados.index(ID_DESCONOCIDO) if ID_DESCONOCIDO in ids_reales_ordenados else 0

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
        "precision_por_locutor": precision_por_locutor,
        "ids_evaluados": ids_reales_ordenados,
        "matriz_confusion": matriz.tolist(),
        "detalles": detalles,
    }

    if verbose:
        _imprimir_resumen(reporte)

    if guardar_matriz:
        _guardar_matriz_confusion(matriz, ids_reales_ordenados, precision_global, identificador.umbral)
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
        etiqueta = "DESCONOCIDO" if id_locutor == ID_DESCONOCIDO else f"locutor {id_locutor:02d}"
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
```

**Ejecutar:**

```bash
python -m src.evaluar
```

**Validación de la tarea:**
- Se genera `resultados/matriz_confusion.png` con la matriz visualizada.
- Se genera `resultados/reporte_evaluacion.json` con métricas detalladas.
- La precisión global reportada refleja el rendimiento real del sistema.

**Resultado esperado con 3 locutores:** precisión global superior al 85-90%.

---

### Tarea 4.7 — Calibrar el umbral de desconocido

**Qué hacer:** ejecutar la evaluación con distintos umbrales para encontrar el valor óptimo que maximiza la precisión global, especialmente en la detección de desconocidos.

**Crear el archivo `src/calibrar_umbral.py`:**

```python
"""
Calibración del umbral de LLR.
Prueba distintos valores y grafica cómo cambia la precisión del sistema.
"""

import json
import numpy as np
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
        print(f"\nProbando umbral = {umbral:.2f} ...")
        reporte = evaluar(umbral=umbral, guardar_matriz=False, verbose=False)
        if reporte is None:
            print("Sin muestras de prueba.")
            return

        resultados.append({
            "umbral": umbral,
            "precision_global": reporte["precision_global"],
            "precision_por_locutor": reporte["precision_por_locutor"],
        })
        print(f"  Precisión global: {reporte['precision_global'] * 100:.2f}%")

    # Mejor umbral
    mejor = max(resultados, key=lambda r: r["precision_global"])
    print("\n" + "=" * 60)
    print(f"  MEJOR UMBRAL: {mejor['umbral']:.2f} → {mejor['precision_global'] * 100:.2f}%")
    print("=" * 60)
    print(f"\nActualiza UMBRAL_DESCONOCIDO en src/config.py con este valor.")

    # Guardar resultados
    ruta_json = CARPETA_RESULTADOS / "calibracion_umbral.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

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
    print(f"Curva guardada en: {ruta}")


if __name__ == "__main__":
    calibrar()
```

**Ejecutar:**

```bash
python -m src.calibrar_umbral
```

**Validación de la tarea:**
- Se ejecuta la evaluación con al menos 30 valores de umbral.
- Se genera `resultados/curva_calibracion.png` con la gráfica.
- Se identifica el umbral óptimo.
- Actualizar `UMBRAL_DESCONOCIDO` en `config.py` con el valor óptimo encontrado.
- Ejecutar `python -m src.evaluar` una última vez para obtener la matriz de confusión definitiva.

---

## 8. Entregables de la Etapa 4

Al finalizar esta etapa se debe contar con:

- Ampliación de `src/config.py` con parámetros del identificador.
- Módulo `src/identifier.py` con la clase `Identificador` y `ResultadoIdentificacion`.
- Script `src/grabar_prueba.py` para grabar muestras nuevas.
- Módulo `src/evaluar.py` con generación de matriz de confusión.
- Script `src/calibrar_umbral.py` con curva de calibración.
- Carpeta `pruebas/` con muestras nuevas de locutores registrados y desconocidos.
- Archivo `resultados/matriz_confusion.png` (entregable clave para la defensa).
- Archivo `resultados/curva_calibracion.png`.
- Archivo `resultados/reporte_evaluacion.json`.
- Umbral óptimo actualizado en `config.py`.
- Commit en GitHub con el mensaje "Etapa 4 completada: identificación de locutor".

---

## 9. Checklist de validación de la etapa

Antes de pasar a la Etapa 5, verificar:

- [ ] `python -m src.identifier <archivo_entrenamiento>` reconoce correctamente al locutor.
- [ ] `python -m src.identifier <archivo_prueba>` funciona sobre muestras nuevas.
- [ ] La carpeta `pruebas/` contiene muestras nuevas de todos los locutores + desconocidos.
- [ ] `python -m src.evaluar` genera la matriz de confusión sin errores.
- [ ] La precisión global con 3 locutores es superior al 85%.
- [ ] Al menos el 60% de los desconocidos son correctamente clasificados como ID = 0.
- [ ] `python -m src.calibrar_umbral` produce la curva de calibración.
- [ ] El umbral óptimo está aplicado en `config.py`.
- [ ] Los cambios están subidos al repositorio en GitHub.

---

## 10. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| Precisión global < 70% en locutores registrados | Grabaciones de prueba muy distintas a las de entrenamiento (otro micrófono, otro ambiente) | Regrabar el conjunto de prueba en las mismas condiciones que el entrenamiento. |
| Todos los desconocidos son clasificados como locutor registrado | Umbral demasiado bajo (o negativo) | Ejecutar la calibración y subir el umbral hasta que los desconocidos se detecten. |
| Los propios locutores son clasificados como desconocidos | Umbral demasiado alto | Bajar el umbral. Suele estar entre 0 y 2 en LLR con MFCC + CMN. |
| La identificación tarda más de 1 segundo | Los modelos se cargan cada vez | Usar una instancia única de `Identificador()` en lugar de crearla en cada llamada. |
| El LLR está siempre negativo | El UBM es más general que los modelos individuales, lo que puede ser correcto | Interpretar en términos relativos: el mejor candidato sigue teniendo el LLR más alto (aunque sea "menos negativo"). |
| Un locutor tiene precisión mucho más baja que los otros | Sus grabaciones de entrenamiento o prueba son de peor calidad | Revisar visualmente sus MFCC; regrabar si es necesario. |
| La matriz de confusión no se guarda | Falta backend gráfico | Añadir `matplotlib.use("Agg")` al inicio del script si se ejecuta sin ventana. |

---

## 11. Recomendaciones adicionales

**Para la memoria y defensa:**

- La **matriz de confusión** es el gráfico más importante del proyecto. Debe estar en la primera página de resultados de la memoria y en las diapositivas. Explica cada fila y columna.
- Prepara una tabla con la precisión global obtenida a distintos tamaños del dataset (3, 10, 20 locutores). Es evidencia de rigor experimental.
- La **curva de calibración** demuestra que el umbral no se eligió arbitrariamente: se optimizó empíricamente.

**Sobre la evaluación honesta:**

- Nunca uses las mismas grabaciones para entrenar y evaluar. Los resultados serían artificialmente altos y el tribunal lo detectará al leer el código.
- Si es posible, involucra a al menos 3-5 personas distintas como "desconocidos". Cuantos más, más robusto será el umbral.

**Consejo de expositor:**

- Pregunta clásica del tribunal: *"¿por qué usa LLR en lugar de log-verosimilitud directa?"*. Respuesta: el LLR compensa el efecto del canal y del ruido de fondo, haciendo que las puntuaciones sean comparables entre muestras. Además, el UBM da un mecanismo natural para rechazar voces desconocidas.

- Otra pregunta típica: *"¿qué haría el sistema si dos personas hablan a la vez?"*. Respuesta honesta: el sistema no está diseñado para separación de fuentes; asignaría el ID del locutor con mayor peso energético en la mezcla. Es una limitación conocida y una posible línea de trabajo futuro.

---

## 12. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 5 — Funcionamiento en Tiempo Real**, cuyo plan de implementación se desarrollará en un documento aparte.

En la Etapa 5 se sustituirá el archivo de audio como entrada por un stream continuo del micrófono, y se añadirá un detector de actividad vocal (VAD) más avanzado que decida cuándo procesar. El identificador construido aquí se reutilizará sin modificaciones, cargándolo una sola vez al arrancar.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
