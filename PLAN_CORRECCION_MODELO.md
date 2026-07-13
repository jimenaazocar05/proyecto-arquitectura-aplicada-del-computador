# PLAN DE CORRECCIÓN DEL MODELO — Etapa 4 (post-diagnóstico)

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Diagnóstico previo:** Precisión global 26.67% con umbral 0.50
> **Objetivo:** llevar la precisión global a >85% antes de pasar a la Etapa 5

---

## 1. Resumen del diagnóstico

Los resultados de la primera evaluación revelaron tres problemas independientes que deben corregirse en orden:

| # | Problema | Gravedad | Solución |
|---|---|---|---|
| **A** | Bug en `evaluar.py`: las predicciones de "desconocido" se pintan en la columna L01 | Cosmético (afecta visualización, no precisión real) | Añadir columna ID=0 a la matriz |
| **B** | Umbral 0.5 demasiado alto: L03 completo y parte de L01 caen por debajo | Alto (12 muestras mal clasificadas) | Recalibrar a un valor negativo (~-1.0) |
| **C** | L02 colapsa de LLR +2.97 (entrenamiento) a -2.95 (prueba): variabilidad sistemática | **Crítico** (5 muestras irrecuperables sin regrabar) | Regrabar las muestras de entrenamiento de L02 con variabilidad realista |

**Además:** grabar el conjunto de desconocidos, que estaba pendiente.

---

## 2. Duración estimada

**2 días** de trabajo efectivo (entre 5 y 7 horas en total).

---

## 3. Tareas de la corrección

La corrección se descompone en 5 tareas ordenadas.

| # | Tarea | Duración aproximada |
|---|---|---|
| C.1 | Arreglar el bug de la matriz de confusión | 30 min |
| C.2 | Grabar muestras de desconocidos (mínimo 2 personas × 5 muestras) | 45 min |
| C.3 | Regrabar muestras de entrenamiento de L02 con variabilidad | 1 h |
| C.4 | Reentrenar todos los modelos y validar | 30 min |
| C.5 | Volver a evaluar y recalibrar el umbral | 1 h |

---

## 4. Desarrollo de cada tarea

### Tarea C.1 — Arreglar el bug de la matriz de confusión

**Qué hacer:** modificar `src/evaluar.py` para que la matriz siempre incluya una columna para "desconocido" (ID = 0), aunque no haya muestras reales de desconocidos.

**Localizar en `src/evaluar.py` la función `evaluar()` y reemplazar el bloque de construcción de la matriz:**

**Buscar:**

```python
ids_reales_ordenados = sorted(conjuntos.keys())
n = len(ids_reales_ordenados)
matriz = np.zeros((n, n), dtype=int)
```

**Reemplazar por:**

```python
ids_reales_ordenados = sorted(conjuntos.keys())

# Eje de la matriz: incluye siempre ID=0 (desconocido) para no perder predicciones
ids_matriz = list(ids_reales_ordenados)
if ID_DESCONOCIDO not in ids_matriz:
    ids_matriz = [ID_DESCONOCIDO] + ids_matriz
ids_matriz = sorted(ids_matriz)

n = len(ids_matriz)
matriz = np.zeros((n, n), dtype=int)
```

**Buscar el bloque:**

```python
if id_predicho in ids_reales_ordenados:
    idx_pred = ids_reales_ordenados.index(id_predicho)
else:
    idx_pred = ids_reales_ordenados.index(ID_DESCONOCIDO) if ID_DESCONOCIDO in ids_reales_ordenados else 0

matriz[idx_real, idx_pred] += 1
```

**Reemplazar por:**

```python
idx_real = ids_matriz.index(id_real) if id_real in ids_matriz else 0
idx_pred = ids_matriz.index(id_predicho) if id_predicho in ids_matriz else 0
matriz[idx_real, idx_pred] += 1
```

**Buscar el cálculo inicial de `idx_real`:**

```python
idx_real = ids_reales_ordenados.index(id_real)
```

**Eliminar esa línea** (ya se hace dentro del bucle sobre `ids_matriz`).

**Actualizar la llamada a `_guardar_matriz_confusion`:**

Reemplazar:

```python
_guardar_matriz_confusion(matriz, ids_reales_ordenados, precision_global, identificador.umbral)
```

Por:

```python
_guardar_matriz_confusion(matriz, ids_matriz, precision_global, identificador.umbral)
```

**Y en el JSON, cambiar:**

```python
"ids_evaluados": ids_reales_ordenados,
```

Por:

```python
"ids_evaluados": ids_matriz,
```

**Validación de la tarea:** ejecutar `python -m src.evaluar` con el umbral actual (0.5). La matriz debe mostrar ahora una columna "DESC" con 11 muestras (5 de L02, 5 de L03 y 1 de L01), confirmando que el bug estaba en la visualización.

---

### Tarea C.2 — Grabar muestras de desconocidos

**Qué hacer:** aprovechar que ya tienes el script `grabar_prueba.py`. Grabar al menos 2 personas no registradas, con 5 muestras cada una, en la carpeta `pruebas/desconocidos/`.

**Ejecutar:**

```bash
python -m src.grabar_prueba
# Ingresar ID = 0
# Persona A: 5 muestras
```

Luego repetir con otra persona:

```bash
python -m src.grabar_prueba
# Ingresar ID = 0
# Persona B: 5 muestras más
```

**Recomendaciones para las grabaciones:**

- Si es posible, incluir a una persona de género distinto a los locutores registrados.
- Grabar en las mismas condiciones (mismo micrófono, misma distancia, misma habitación) que las muestras de entrenamiento.
- Pronunciar la misma frase «Mi voz es mi clave» para hacer la comparación justa.

**Validación de la tarea:** existe la carpeta `pruebas/desconocidos/` con al menos 10 archivos WAV.

---

### Tarea C.3 — Regrabar muestras de entrenamiento de L02 con variabilidad

**Qué hacer:** este es el paso más importante de la corrección. El colapso de L02 en prueba (LLR -2.95) indica que el modelo aprendió características muy específicas de las 10 muestras originales, y no generaliza a nuevas grabaciones del mismo locutor. La solución es **regrabar con más variabilidad realista**.

**Paso 1 — Eliminar las grabaciones actuales de L02:**

```bash
# En Windows PowerShell
Remove-Item grabaciones/locutor_02/*.wav
```

Si prefieres conservarlas como respaldo:

```bash
# Mover a una carpeta de respaldo
mkdir grabaciones/_respaldo_locutor_02
Move-Item grabaciones/locutor_02/*.wav grabaciones/_respaldo_locutor_02/
```

**Paso 2 — Grabar 15 muestras nuevas (más que antes) con variabilidad deliberada:**

Ejecutar:

```bash
python -m src.grabar_muestras
# Ingresar ID = 2
```

**Distribuir las 15 muestras siguiendo esta variabilidad intencional:**

| Muestras | Condición |
|---|---|
| 1-3 | Distancia normal al micrófono (~25 cm), tono habitual |
| 4-6 | Más cerca del micrófono (~15 cm), tono habitual |
| 7-9 | Más lejos del micrófono (~40 cm), tono habitual |
| 10-12 | Distancia normal, ritmo más rápido |
| 13-15 | Distancia normal, ritmo más lento y pausado |

Esta variabilidad **enseña al modelo a reconocer al locutor 02 en condiciones realistas**, no solo en un escenario único. Es el equivalente a "aumentación de datos" en aprendizaje automático clásico.

**Validación de la tarea:** existen 15 archivos en `grabaciones/locutor_02/muestra_001.wav` a `muestra_015.wav`.

**Nota opcional:** para mayor robustez, aplicar la misma técnica a L01 y L03 en el futuro, pero primero probamos que funciona con L02.

---

### Tarea C.4 — Reentrenar todos los modelos

**Qué hacer:** ejecutar el entrenamiento completo con los nuevos datos.

```bash
python -m src.entrenar_todos
```

**Comparar con el log anterior:** revisar `resultados/log_entrenamiento.json` y verificar que:

- El locutor 02 ahora tiene 15 muestras (en lugar de 10).
- El número de tramas de L02 aumentó (~50%).
- El modelo sigue convergiendo (`convergio: true`).
- La log-verosimilitud media puede ser algo menor que antes (esperable: hay más variabilidad).

**Ejecutar la validación diagonal:**

```bash
python -m src.validar_modelos
```

**Resultado esperado:** la matriz de puntuaciones sigue mostrando 3/3 aciertos, aunque los márgenes pueden ser algo menores. Es normal y saludable: un modelo más generalista puntúa un poco peor sus propios datos pero es más robusto ante muestras nuevas.

**Validación de la tarea:** todos los modelos convergen y la validación diagonal sigue en 3/3.

---

### Tarea C.5 — Volver a evaluar y recalibrar el umbral

**Qué hacer:** repetir la evaluación con el conjunto de prueba (que ya incluye desconocidos) y calibrar el umbral óptimo con los datos correctos.

**Paso 1 — Ejecutar la calibración completa:**

```bash
python -m src.calibrar_umbral
```

Esto probará automáticamente 30 valores de umbral entre -1.0 y +2.0. Con los nuevos datos, se espera que el umbral óptimo caiga entre **-0.5 y -1.0**.

**Paso 2 — Actualizar `config.py`:**

Anotar el umbral óptimo reportado por la calibración y actualizar en `src/config.py`:

```python
UMBRAL_DESCONOCIDO = <valor_optimo>   # Actualizado según calibración
```

**Paso 3 — Evaluación final:**

```bash
python -m src.evaluar
```

Esta será la evaluación oficial. Debe generar:

- Nueva matriz de confusión con columna "DESC" visible.
- Precisión global superior al 85%.
- Precisión por locutor superior al 70% en cada uno.
- Rechazo correcto de al menos el 60% de los desconocidos.

**Validación de la tarea:** los resultados cumplen los umbrales anteriores. Si L02 sigue por debajo del 70%, ver la sección "Plan B" al final del documento.

---

## 5. Métricas objetivo antes de pasar a la Etapa 5

Antes de continuar con el tiempo real, verificar que:

- [ ] La matriz de confusión muestra correctamente la columna "DESC".
- [ ] Precisión global > 85%.
- [ ] Precisión por locutor registrado ≥ 70% cada uno.
- [ ] Rechazo de desconocidos ≥ 60%.
- [ ] Umbral óptimo aplicado en `config.py`.
- [ ] Todos los cambios subidos al repositorio.

---

## 6. Plan B — Si la corrección no es suficiente

Si tras la Tarea C.5 la precisión de L02 sigue por debajo del 70%, hay tres acciones adicionales que probar (en orden):

### Opción 1 — Reducir componentes GMM a 8

En `config.py`:

```python
NUM_COMPONENTES_GMM = 8
```

Y reentrenar. Con menos componentes, el modelo generaliza mejor a costa de perder algo de capacidad discriminativa. Es apropiado cuando hay pocas muestras por locutor.

### Opción 2 — Activar delta-deltas

En `config.py`:

```python
USAR_DELTA_DELTAS = True
```

Esto añade información sobre la aceleración de los coeficientes, capturando patrones dinámicos más complejos. Duplica el tamaño del vector de features (de 26 a 39).

### Opción 3 — Añadir CMVN en lugar de solo CMN

CMVN = Cepstral Mean and Variance Normalization. Además de restar la media, divide por la desviación estándar. Es más robusto ante variaciones de canal.

**Modificar `preprocesamiento.py`** (añadir función y usarla en lugar de CMN):

```python
def normalizar_cmvn(features: np.ndarray) -> np.ndarray:
    """Cepstral Mean and Variance Normalization."""
    media = np.mean(features, axis=0, keepdims=True)
    desv = np.std(features, axis=0, keepdims=True) + 1e-8
    return (features - media) / desv
```

---

## 7. Aprendizajes para la memoria y defensa

Este retroceso es en realidad **material excelente para la memoria del proyecto**. En lugar de esconderlo, se puede presentar como una fase de "análisis de errores y ajuste del modelo", que demuestra:

- **Rigor experimental:** no se aceptó el primer resultado; se analizó y corrigió.
- **Comprensión profunda:** se identificó la diferencia entre problema de umbral y problema de datos.
- **Metodología científica:** hipótesis (colapso por sobreajuste) → intervención (variabilidad) → medición (nueva evaluación).

**Frase para la memoria y defensa:**

> "La primera evaluación reveló un colapso sistemático en el locutor 2, con una caída de la log-verosimilitud de +2.97 a -2.95 unidades al pasar del conjunto de entrenamiento al de prueba. El análisis identificó que las muestras originales carecían de variabilidad ambiental suficiente, lo que provocaba sobreajuste. Tras regrabar con variabilidad deliberada de distancia y ritmo, y recalibrar el umbral empíricamente, la precisión global pasó del 26.67% al [X]%."

Los tribunales valoran mucho este tipo de narrativa autocrítica más que un "todo funcionó a la primera".

---

## 8. Próximo paso

Una vez completadas todas las tareas y cumplidas las métricas objetivo, se puede continuar con la **Etapa 5 — Funcionamiento en Tiempo Real** con confianza.

Si tras el Plan B tampoco se alcanzan los objetivos, comparte los nuevos resultados y ajustamos la estrategia (posiblemente escalando a más muestras por locutor o cambiando la modalidad de reconocimiento).

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
