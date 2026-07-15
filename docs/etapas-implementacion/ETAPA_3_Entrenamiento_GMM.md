# ETAPA 3 — Entrenamiento de Modelos GMM por Locutor

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 3
> **Prerrequisito:** Etapa 2 completada (pipeline MFCC funcional sobre todo el dataset)

---

## 1. Objetivo de la etapa

Construir el módulo de entrenamiento que, a partir de las muestras de audio de cada locutor, produce un modelo estadístico GMM (Gaussian Mixture Model) capaz de representar sus características vocales. Al final de esta etapa, cada locutor tendrá asociado un archivo `.pkl` con su modelo entrenado, y el sistema estará listo para realizar identificación en la Etapa 4.

Al final de esta etapa, el sistema debe poder:

- Cargar todas las muestras de un locutor, extraer sus MFCC y entrenar un GMM.
- Guardar el modelo entrenado en formato serializado (`.pkl`).
- Entrenar automáticamente los modelos de todos los locutores registrados.
- Registrar métricas del entrenamiento (convergencia, log-verosimilitud, tiempo).
- Cargar modelos previamente entrenados desde disco.
- Manejar el caso del locutor "desconocido" (ID = 0) mediante un modelo universal (UBM).

---

## 2. Justificación

Esta es la etapa donde el sistema pasa de "procesar datos" a "aprender". El GMM entrenado es el **conocimiento** del sistema; sin él, no hay reconocimiento posible.

**El entrenamiento define la calidad final del sistema.** Si los modelos están mal entrenados (pocos datos, mala inicialización, hiperparámetros inadecuados), ni el mejor identificador de la Etapa 4 podrá corregir el error. La calidad de identificación tiene un techo marcado aquí.

**Los modelos se entrenan una vez y se usan miles.** El entrenamiento es costoso (segundos por locutor), pero la identificación en tiempo real requerirá cargar los modelos cientos de veces. Por eso se serializan a disco: se entrenan una vez y se reutilizan.

**El manejo del "desconocido" es no trivial.** ¿Qué hace el sistema cuando alguien no registrado habla? Sin un mecanismo específico, siempre asignará el ID del locutor más "parecido", generando falsos positivos. La solución clásica es el **modelo universal de fondo (UBM)**, que representa "voz humana en general".

**Este es el corazón "estadístico" de la defensa.** Explicar qué es una mezcla gaussiana, cómo el algoritmo EM (Expectation-Maximization) ajusta los parámetros, y por qué GMM funciona bien con MFCC, es lo que demuestra dominio real de la asignatura.

---

## 3. Fundamento teórico breve

Un **Gaussian Mixture Model (GMM)** modela una distribución compleja como una suma ponderada de N distribuciones gaussianas simples. Cada gaussiana tiene tres parámetros:

- **Media (μ):** el "centro" de la distribución en el espacio de MFCC.
- **Covarianza (Σ):** cómo se dispersan los datos alrededor de la media.
- **Peso (w):** cuánto contribuye esta gaussiana al modelo total.

La probabilidad de un vector MFCC x según el modelo es:

**p(x) = Σᵢ wᵢ · N(x | μᵢ, Σᵢ)**

donde N(·) es la función de densidad gaussiana. El modelo se entrena mediante el algoritmo **Expectation-Maximization (EM)**, que ajusta iterativamente los parámetros para maximizar la verosimilitud de los datos.

**¿Por qué GMM funciona bien para voz?** Los MFCC de una persona no forman una nube compacta: se agrupan en varios "clusters" que corresponden a distintos fonemas (vocales, fricativas, oclusivas...). El GMM captura esta estructura con una gaussiana por cluster, aproximadamente.

**Universal Background Model (UBM):** para detectar locutores desconocidos, se entrena un GMM adicional con datos mezclados de todos los locutores (o de un dataset público). Este modelo representa "cualquier voz humana". Si una nueva muestra se parece más al UBM que a cualquier modelo específico, se considera desconocida.

---

## 4. Decisiones técnicas previas

Se fijan los parámetros del entrenamiento que se usarán en el proyecto:

| Parámetro | Valor elegido | Justificación |
|---|---|---|
| Componentes gaussianos por modelo | **16** | Estándar en la literatura para identificación de locutor con 10-20 muestras. |
| Tipo de covarianza | **diagonal** | Reduce parámetros a estimar; suficiente para MFCC (que están decorrelacionados por el DCT). |
| Iteraciones máximas de EM | **200** | Suficiente para converger; el algoritmo suele parar antes por tolerancia. |
| Tolerancia de convergencia | **0.001** | Estándar de `scikit-learn`. Balance entre precisión y tiempo. |
| Inicialización | **k-means (k-means++)** | Mejor que aleatoria: parte de centros ya bien distribuidos. |
| Semilla aleatoria | **42** | Reproducibilidad total del entrenamiento. |
| Modelo del "desconocido" (UBM) | **32 componentes** | El doble que los modelos individuales, para cubrir mayor variabilidad. |
| Formato de serialización | **pickle (`.pkl`)** | Simple, nativo de Python, adecuado para `scikit-learn`. |
| Log de entrenamiento | **JSON en `resultados/`** | Estructurado, fácil de inspeccionar. |

---

## 5. Duración estimada

**4 días** de trabajo efectivo (entre 10 y 14 horas en total).

---

## 6. Tareas de la Etapa 3

La etapa se descompone en 6 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| 3.1 | Ampliar `config.py` con parámetros de entrenamiento | 30 min |
| 3.2 | Implementar función de recolección de features por locutor | 1.5 h |
| 3.3 | Implementar el entrenamiento de un modelo GMM individual | 2 h |
| 3.4 | Crear módulo de serialización y carga de modelos | 1.5 h |
| 3.5 | Implementar el entrenamiento masivo y el UBM | 2.5 h |
| 3.6 | Validación de los modelos entrenados | 2 h |

---

## 7. Desarrollo de cada tarea

### Tarea 3.1 — Ampliar `config.py` con parámetros de entrenamiento

**Qué hacer:** añadir al archivo de configuración los parámetros que controlan el algoritmo de entrenamiento y las rutas de serialización.

**Añadir al final de `src/config.py`:**

```python
# ============================================================
# PARÁMETROS DEL MODELO GMM
# ============================================================
NUM_COMPONENTES_GMM = 16            # Componentes gaussianos por modelo individual
NUM_COMPONENTES_UBM = 32            # Componentes para el modelo universal
TIPO_COVARIANZA = "diag"            # "diag" | "full" | "tied" | "spherical"
MAX_ITERACIONES_EM = 200            # Iteraciones máximas del algoritmo EM
TOLERANCIA_CONVERGENCIA = 1e-3      # Umbral de parada del EM
METODO_INICIALIZACION = "kmeans"    # "kmeans" | "random"
SEMILLA_ALEATORIA = 42              # Reproducibilidad

# ============================================================
# ENTRENAMIENTO
# ============================================================
MIN_MUESTRAS_POR_LOCUTOR = 3        # Mínimo aceptable para entrenar
NOMBRE_MODELO_UBM = "ubm.pkl"       # Nombre del archivo del UBM
NOMBRE_LOG_ENTRENAMIENTO = "log_entrenamiento.json"
```

**Validación de la tarea:** ejecutar `python -c "from src.config import NUM_COMPONENTES_GMM; print(NUM_COMPONENTES_GMM)"` imprime `16`.

---

### Tarea 3.2 — Implementar función de recolección de features por locutor

**Qué hacer:** crear una función que recorra la carpeta de un locutor, procese todas sus muestras con el pipeline de la Etapa 2 y devuelva una matriz consolidada de features lista para entrenar.

**Crear el archivo `src/dataset.py`:**

```python
"""
Módulo de gestión del dataset.
Provee funciones para recolectar features desde las carpetas de grabaciones.
"""

import numpy as np
from pathlib import Path
from typing import Tuple

from src.config import CARPETA_GRABACIONES, MIN_MUESTRAS_POR_LOCUTOR
from src.feature_extractor import extraer_features


def listar_locutores() -> list[int]:
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
```

**Ejecutar la prueba:**

```bash
python -m src.dataset
```

**Validación de la tarea:**
- Se lista correctamente cada locutor con su cantidad de muestras.
- El shape reportado tiene 26 columnas (13 MFCC + 13 deltas).
- El número total de tramas por locutor es de al menos varios miles (10 muestras × ~300 tramas cada una).

---

### Tarea 3.3 — Implementar el entrenamiento de un modelo GMM individual

**Qué hacer:** crear la función central que toma las features de un locutor y produce un modelo GMM entrenado con métricas del proceso.

**Crear el archivo `src/trainer.py`:**

```python
"""
Módulo de entrenamiento de modelos GMM.
Provee funciones para entrenar un modelo por locutor.
"""

import time
import numpy as np
from sklearn.mixture import GaussianMixture

from src.config import (
    NUM_COMPONENTES_GMM,
    NUM_COMPONENTES_UBM,
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
```

**Ejecutar la prueba:**

```bash
python -m src.trainer
```

**Validación de la tarea:**
- El modelo converge (`convergio = True`) en menos de 200 iteraciones.
- La log-verosimilitud es un número finito (típicamente entre -50 y 50 para MFCC normalizados).
- El tiempo de entrenamiento por locutor es de pocos segundos.

---

### Tarea 3.4 — Crear módulo de serialización y carga de modelos

**Qué hacer:** implementar funciones para guardar los modelos entrenados en disco y cargarlos posteriormente. Esto permite entrenar una vez y usar muchas.

**Crear el archivo `src/modelos_io.py`:**

```python
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


def listar_modelos_disponibles() -> list[int]:
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
```

**Validación de la tarea:** el script se ejecuta sin errores y reporta que aún no hay modelos entrenados (correcto, se harán en la siguiente tarea).

---

### Tarea 3.5 — Implementar el entrenamiento masivo y el UBM

**Qué hacer:** crear el script principal que entrena en un solo comando los modelos de todos los locutores registrados, además del UBM para el locutor desconocido. Registra un log JSON completo del proceso.

**Crear el archivo `src/entrenar_todos.py`:**

```python
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
```

**Ejecutar:**

```bash
python -m src.entrenar_todos
```

**Validación de la tarea:**
- Se crean los archivos `modelos/locutor_XX.pkl` para cada locutor registrado.
- Se crea `modelos/ubm.pkl`.
- Se crea `resultados/log_entrenamiento.json` con toda la información.
- Todos los modelos convergen (`convergio: true`).
- El tiempo total es razonable (menos de 1 minuto para 3-5 locutores).

---

### Tarea 3.6 — Validación de los modelos entrenados

**Qué hacer:** crear un script de verificación que confirme que los modelos entrenados se pueden cargar correctamente y que producen puntuaciones coherentes: cada modelo debe puntuar más alto sus propias muestras que las de otros locutores.

**Crear el archivo `src/validar_modelos.py`:**

```python
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


def matriz_de_puntuaciones() -> np.ndarray:
    """
    Genera una matriz cuadrada donde M[i, j] es la puntuación
    del modelo del locutor i evaluado sobre las features del locutor j.

    La diagonal debe tener los valores más altos por columna.
    """
    ids = listar_modelos_disponibles()
    if not ids:
        print("No hay modelos entrenados. Ejecuta primero `python -m src.entrenar_todos`.")
        return

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


def imprimir_matriz(matriz: np.ndarray, ids: list[int]) -> None:
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
    matriz, ids = matriz_de_puntuaciones()
    imprimir_matriz(matriz, ids)
```

**Ejecutar:**

```bash
python -m src.validar_modelos
```

**Resultado esperado:** una matriz cuadrada donde los valores de la diagonal (modelo Li evaluado sobre features del locutor i) son los más altos de cada fila. Ejemplo con 3 locutores:

```
          L01     L02     L03
  L01   [ 12.34]   8.11    7.02
  L02     6.55   [11.89]   7.14
  L03     7.20    6.90   [12.02]

Modelos que puntúan mejor su propio locutor: 3/3
VALIDACIÓN CORRECTA: cada modelo reconoce su locutor.
```

**Validación final de la etapa:**
- Todos los modelos puntúan más alto sus propias muestras que las de otros locutores.
- La diferencia entre la diagonal y los valores fuera es notable (varias unidades).
- No hay NaN, Inf ni errores de carga de modelos.

---

## 8. Entregables de la Etapa 3

Al finalizar esta etapa se debe contar con:

- Ampliación de `src/config.py` con parámetros de entrenamiento.
- Módulo `src/dataset.py` de recolección de features por locutor.
- Módulo `src/trainer.py` con la función de entrenamiento GMM.
- Módulo `src/modelos_io.py` de serialización y carga.
- Script `src/entrenar_todos.py` para el entrenamiento masivo.
- Script `src/validar_modelos.py` de validación rápida.
- Archivos `modelos/locutor_XX.pkl` para cada locutor registrado.
- Archivo `modelos/ubm.pkl` con el modelo universal.
- Archivo `resultados/log_entrenamiento.json` con métricas del proceso.
- Commit en GitHub con el mensaje "Etapa 3 completada: entrenamiento de modelos GMM".

---

## 9. Checklist de validación de la etapa

Antes de pasar a la Etapa 4, verificar:

- [ ] `python -m src.dataset` lista correctamente todos los locutores con sus tramas.
- [ ] `python -m src.trainer` entrena un modelo de prueba sin errores.
- [ ] `python -m src.entrenar_todos` genera un `.pkl` por locutor y el UBM.
- [ ] Todos los modelos reportan `convergio: true` en el log JSON.
- [ ] `python -m src.validar_modelos` muestra 100% de aciertos en la matriz diagonal.
- [ ] La diferencia entre la diagonal y los valores no diagonales es de al menos 2 unidades.
- [ ] El archivo `resultados/log_entrenamiento.json` existe y contiene métricas de todos los modelos.
- [ ] Los cambios están subidos al repositorio en GitHub.

---

## 10. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| `ConvergenceWarning: Initialization did not converge` | Pocas muestras o inicialización desafortunada | Reducir componentes a 8, aumentar `MAX_ITERACIONES_EM` o cambiar la semilla. |
| Log-verosimilitud extremadamente baja o `-inf` | Covarianzas singulares por datos degenerados | Aumentar `reg_covar` en el trainer (por ejemplo, 1e-4). |
| La diagonal NO tiene los valores más altos | Muestras muy similares entre locutores o CMN mal aplicada | Revisar Etapa 2: asegurarse de que los MFCC de locutores distintos se ven diferentes. |
| Un locutor sistemáticamente pierde contra otro | Grabaciones de mala calidad o muy pocas muestras | Regrabar ese locutor con más variedad o comprobar el nivel del micrófono. |
| El entrenamiento tarda más de 30 s por modelo | Demasiados componentes o `covariance_type="full"` | Reducir a 8 componentes y confirmar que se usa `"diag"`. |
| `ValueError: n_samples < n_components` | Muy pocas tramas para el número de componentes | Grabar más muestras o reducir componentes en `config.py`. |
| El UBM tiene log-verosimilitud parecida a los individuales | Los individuales están sobreajustados | Es esperable: el UBM es más general por diseño. |

---

## 11. Recomendaciones adicionales

**Para la memoria y defensa:**

- Prepara una diapositiva con la fórmula del GMM y una explicación intuitiva del algoritmo EM (paso E: asignar probabilidades, paso M: actualizar parámetros). Los tribunales suelen preguntar.
- Incluye la matriz de puntuaciones de la Tarea 3.6 en la memoria como evidencia de que el sistema discrimina antes incluso de la identificación formal.
- Ten preparado el argumento del UBM: "sin UBM el sistema clasificaría a cualquier persona nueva como uno de los locutores conocidos, generando falsos positivos peligrosos en un escenario real de autenticación".

**Para el trabajo posterior:**

- Si al final del proyecto el sistema no discrimina bien con 16 componentes, prueba con 8 o 32 modificando solo `NUM_COMPONENTES_GMM` en `config.py` y volviendo a entrenar. No requiere cambiar código.
- El log JSON es tu mejor amigo para depurar. Revisa la log-verosimilitud media entre locutores: si un locutor tiene un valor mucho más bajo que los demás, probablemente sus grabaciones tienen problemas.

**Consejo de expositor:**

- Pregunta clásica del tribunal: «¿Por qué GMM y no una red neuronal?». Respuesta: GMM es un modelo generativo probabilístico interpretable, con pocos parámetros, que funciona muy bien con datasets pequeños (10-20 muestras por clase). Las redes neuronales requerirían miles de muestras y no aportan explicabilidad. Además, GMM permite el uso natural del UBM para la clase "desconocida".

- Otra pregunta típica: «¿Por qué covarianza diagonal?». Respuesta: los MFCC ya están decorrelacionados por el DCT en la Etapa 2, así que las covarianzas fuera de la diagonal aportan poca información y multiplicarían por 13 el número de parámetros a estimar, haciendo el modelo mucho más pesado y propenso a sobreajuste.

---

## 12. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 4 — Identificación de Locutor a partir de Archivo**, cuyo plan de implementación se desarrollará en un documento aparte.

En la Etapa 4 se utilizarán los modelos entrenados para construir el identificador principal: dado un archivo de audio nuevo, decidir cuál de los locutores lo pronunció (o si es desconocido). Se generará la **matriz de confusión** del sistema, que es el entregable clave para la defensa.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
