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
