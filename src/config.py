"""
Configuración global del proyecto.
Todos los parámetros del sistema se centralizan aquí.
"""

from pathlib import Path

# ============================================================
# RUTAS DEL PROYECTO
# ============================================================
RAIZ = Path(__file__).parent.parent
CARPETA_GRABACIONES = RAIZ / "grabaciones"
CARPETA_MODELOS = RAIZ / "modelos"
CARPETA_PRUEBAS = RAIZ / "pruebas"
CARPETA_RESULTADOS = RAIZ / "resultados"

# ============================================================
# PARÁMETROS DE AUDIO
# ============================================================
FRECUENCIA_MUESTREO = 16000       # Hz
CANALES = 1                        # Mono
PROFUNDIDAD_BITS = 16              # bits
DURACION_GRABACION = 3.0           # segundos

# ============================================================
# LOCUTORES
# ============================================================
NUMERO_MAXIMO_LOCUTORES = 20
NUMERO_LOCUTORES_ACTIVOS = 3       # Locutores actualmente en uso
MUESTRAS_POR_LOCUTOR = 10          # Se ajusta según pruebas

# ============================================================
# MICRÓFONO
# ============================================================
# None = usar dispositivo por defecto del sistema.
# Cambiar por el índice devuelto por sd.query_devices() si es necesario.
DISPOSITIVO_ENTRADA = None

# ============================================================
# PARÁMETROS DE EXTRACCIÓN MFCC
# ============================================================
NUM_MFCC = 13                       # Número de coeficientes cepstrales
USAR_DELTAS = True                  # Incluir derivadas de primer orden
USAR_DELTA_DELTAS = False           # Incluir derivadas de segundo orden

LONGITUD_TRAMA_MS = 25              # Longitud de cada trama en milisegundos
SOLAPE_TRAMA_MS = 10                # Solape entre tramas en milisegundos

# Derivados (se calculan a partir de FRECUENCIA_MUESTREO)
LONGITUD_TRAMA_MUESTRAS = int(FRECUENCIA_MUESTREO * LONGITUD_TRAMA_MS / 1000)
SOLAPE_TRAMA_MUESTRAS = int(FRECUENCIA_MUESTREO * SOLAPE_TRAMA_MS / 1000)

# Parámetros del banco de filtros
NUM_FILTROS_MEL = 26                # Número de filtros triangulares Mel
COEF_PREENFASIS = 0.97              # Coeficiente del filtro de pre-énfasis

# ============================================================
# PREPROCESAMIENTO
# ============================================================
APLICAR_CMN = True                  # Cepstral Mean Normalization
APLICAR_VAD = True                  # Voice Activity Detection simple
UMBRAL_VAD_DB = -35                 # Umbral en dB para detectar silencio

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

# ============================================================
# PARÁMETROS DEL IDENTIFICADOR
# ============================================================
USAR_LLR = True                     # True: LLR (score - UBM). False: LL directo.
UMBRAL_DESCONOCIDO = -0.10            # LLR mínimo para aceptar identificación
ID_DESCONOCIDO = 0                  # ID reservado para locutor desconocido

# ============================================================
# EVALUACIÓN
# ============================================================
NOMBRE_MATRIZ_CONFUSION_PNG = "matriz_confusion.png"
NOMBRE_REPORTE_EVALUACION = "reporte_evaluacion.json"

# Rango de umbrales a probar durante la calibración
UMBRALES_CALIBRACION = [i * 0.1 for i in range(-10, 21)]   # -1.0 a 2.0 en pasos de 0.1

