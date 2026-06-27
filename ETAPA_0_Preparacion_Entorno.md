# ETAPA 0 — Preparación del Entorno de Trabajo

> **Proyecto:** Sistema de Identificación de Voces Humanas con Interfaz Física
> **Algoritmo:** MFCC + GMM
> **Documento:** Plan de implementación de la Etapa 0

---

## 1. Objetivo de la etapa

Dejar la computadora lista para empezar a programar el sistema de reconocimiento de voz: **Python instalado, entorno virtual creado, dependencias instaladas, repositorio inicializado en Git/GitHub, y verificación de que el micrófono funciona**.

Al final de esta etapa, ejecutar un script de "Hola mundo" del proyecto debe funcionar sin errores.

---

## 2. Justificación

Esta etapa no implementa funcionalidad del sistema, pero es indispensable por tres razones:

**Reproducibilidad académica.** Al entregar el proyecto, el tutor o cualquier evaluador debe poder clonar el repositorio, ejecutar dos comandos y tener el sistema funcionando. Sin un entorno controlado, esto es imposible.

**Evitar conflictos de dependencias.** Instalar librerías globalmente conduce, en pocas semanas, a conflictos de versiones entre proyectos. El entorno virtual aísla este proyecto del resto del sistema.

**Defensa del proyecto.** Un repositorio bien estructurado, con commits frecuentes y un README claro, es un argumento visual de profesionalismo que el tribunal nota inmediatamente.

---

## 3. Duración estimada

**2 días** de trabajo (entre 3 y 5 horas en total).

---

## 4. Tareas de la Etapa 0

La etapa se descompone en 7 tareas ordenadas. Cada una se valida antes de pasar a la siguiente.

| # | Tarea | Duración aproximada |
|---|---|---|
| 0.1 | Verificar instalación de Python | 15 min |
| 0.2 | Crear la carpeta del proyecto y estructura base | 20 min |
| 0.3 | Crear y activar el entorno virtual | 15 min |
| 0.4 | Crear el archivo `requirements.txt` e instalar dependencias | 30 min |
| 0.5 | Verificar el micrófono y dispositivos de audio | 30 min |
| 0.6 | Inicializar el repositorio Git y subir a GitHub | 45 min |
| 0.7 | Crear el README.md y el script `hola_mundo.py` de verificación | 30 min |

---

## 5. Desarrollo de cada tarea

### Tarea 0.1 — Verificar instalación de Python

**Qué hacer:** comprobar que está instalado Python 3.10 o superior. Si no, instalarlo desde [python.org](https://www.python.org/downloads/). En Windows, marcar la opción **"Add Python to PATH"** durante la instalación.

**Comando de verificación:**

```bash
python --version
```

**Resultado esperado:** `Python 3.10.x` o superior.

**Validación de la tarea:** el comando devuelve una versión 3.10 o mayor sin errores.

---

### Tarea 0.2 — Crear la carpeta del proyecto y estructura base

**Qué hacer:** crear la carpeta raíz del proyecto en una ubicación accesible (por ejemplo, `Documentos/Proyectos/`). Usar un nombre corto y sin espacios.

```bash
mkdir reconocimiento_voz
cd reconocimiento_voz
```

Dentro de esa carpeta, crear la estructura inicial de directorios:

```
reconocimiento_voz/
├── src/                    # Código fuente del proyecto
├── grabaciones/            # Muestras de audio por locutor
├── modelos/                # Modelos GMM entrenados (.pkl)
├── pruebas/                # Muestras de validación
├── resultados/             # Matrices de confusión, logs, gráficos
└── docs/                   # Documentación adicional
```

**Comandos para crear la estructura (Linux/Mac):**

```bash
mkdir src grabaciones modelos pruebas resultados docs
```

**Comandos para crear la estructura (Windows PowerShell):**

```powershell
mkdir src, grabaciones, modelos, pruebas, resultados, docs
```

**Validación de la tarea:** ejecutar `ls` (o `dir` en Windows) muestra las 6 carpetas creadas.

---

### Tarea 0.3 — Crear y activar el entorno virtual

**Qué hacer:** crear un entorno Python aislado dentro del proyecto. Esto genera una carpeta `venv/` que contiene una copia de Python específica para este trabajo.

```bash
python -m venv venv
```

**Activar el entorno** (se hace cada vez que se vuelve a trabajar):

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Linux/Mac:** `source venv/bin/activate`

**Validación de la tarea:** después de activar, el prompt de la terminal muestra `(venv)` al inicio de cada línea.

> **Nota:** si en Windows aparece un error de ejecución de scripts en PowerShell, ejecutar una sola vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

---

### Tarea 0.4 — Crear el archivo `requirements.txt` e instalar dependencias

**Qué hacer:** crear un archivo de texto que liste todas las dependencias del proyecto con sus versiones mínimas.

**Crear el archivo `requirements.txt` en la raíz del proyecto con el siguiente contenido:**

```
numpy>=1.24.0
scipy>=1.10.0
sounddevice>=0.4.6
soundfile>=0.12.1
librosa>=0.10.1
scikit-learn>=1.3.0
matplotlib>=3.7.0
pyserial>=3.5
```

**Breve descripción de cada librería:**

| Librería | Uso en el proyecto |
|---|---|
| `numpy` | Operaciones numéricas y manejo de arreglos multidimensionales. |
| `scipy` | Funciones avanzadas de procesamiento de señales y estadística. |
| `sounddevice` | Captura y reproducción de audio en tiempo real desde el micrófono. |
| `soundfile` | Lectura y escritura de archivos `.wav`. |
| `librosa` | Extracción de coeficientes MFCC y análisis de señales de audio. |
| `scikit-learn` | Implementación de los Modelos de Mezcla Gaussiana (GMM). |
| `matplotlib` | Visualización de formas de onda, espectrogramas y matrices de confusión. |
| `pyserial` | Comunicación serial con el microcontrolador Arduino (Etapa 6). |

**Instalar todas las dependencias con un solo comando:**

```bash
pip install -r requirements.txt
```

**Validación de la tarea:** al final de la instalación no aparecen errores en rojo. Ejecutar:

```bash
pip list
```

Debe mostrar todas las librerías listadas.

> **Nota para Linux:** si `sounddevice` falla, instalar primero la dependencia del sistema:
> `sudo apt-get install libportaudio2`

---

### Tarea 0.5 — Verificar el micrófono y dispositivos de audio

**Qué hacer:** comprobar que Python puede acceder al micrófono. Crear un script temporal de prueba.

**Crear el archivo `src/verificar_audio.py`:**

```python
import sounddevice as sd

print("=== Dispositivos de audio disponibles ===\n")
print(sd.query_devices())
print("\n=== Dispositivo de entrada por defecto ===")
print(sd.default.device)
```

**Ejecutar:**

```bash
python src/verificar_audio.py
```

**Resultado esperado:** la consola muestra una lista de dispositivos. El micrófono debe aparecer marcado como dispositivo de entrada.

**Anotar el índice del micrófono** que se vaya a usar; se necesitará en la Etapa 1.

**Validación de la tarea:** el micrófono aparece en la lista y no se producen errores.

---

### Tarea 0.6 — Inicializar el repositorio Git y subir a GitHub

**Qué hacer:** poner el proyecto bajo control de versiones desde el primer día. Esto permite revertir cambios, llevar historial y compartir el código fácilmente con el tutor.

**Paso 1 — Inicializar Git localmente:**

```bash
git init
```

**Paso 2 — Crear el archivo `.gitignore`** en la raíz del proyecto con este contenido:

```
# Entorno virtual
venv/
env/
*.pyc
__pycache__/

# Archivos de audio (pesados, no van al repositorio)
grabaciones/
pruebas/
*.wav

# Modelos entrenados (se regeneran)
modelos/*.pkl

# Resultados generados
resultados/

# Configuración del editor
.vscode/
.idea/
*.swp

# Sistema operativo
.DS_Store
Thumbs.db
```

> **Importante:** el `.gitignore` evita subir archivos pesados (grabaciones de audio) o que se regeneran automáticamente (entornos virtuales, modelos). El repositorio quedará liviano y limpio.

**Paso 3 — Hacer el primer commit:**

```bash
git add .
git commit -m "Etapa 0: estructura inicial del proyecto y entorno configurado"
```

**Paso 4 — Crear el repositorio en GitHub:**

1. Entrar a [github.com](https://github.com) y crear una cuenta si no se tiene.
2. Clic en "New repository".
3. Nombre del repositorio: `reconocimiento-voz-locutores` (o similar).
4. Marcar como **público** o **privado** según preferencia (privado se recomienda hasta la entrega).
5. **NO** marcar la opción de añadir README, .gitignore ni LICENSE (ya están creados localmente).
6. Crear el repositorio.

**Paso 5 — Conectar el repositorio local con GitHub:**

GitHub mostrará las instrucciones. Serán similares a:

```bash
git remote add origin https://github.com/TU_USUARIO/reconocimiento-voz-locutores.git
git branch -M main
git push -u origin main
```

**Validación de la tarea:** al refrescar la página de GitHub, se ven todos los archivos del proyecto subidos.

---

### Tarea 0.7 — Crear el README.md y el script `hola_mundo.py` de verificación

**Qué hacer:** crear dos archivos finales que demuestren que el entorno está funcional y documentado.

**Paso 1 — Crear el archivo `README.md`** en la raíz del proyecto:

```markdown
# Sistema de Identificación de Voces Humanas con Interfaz Física

Proyecto de fin de curso de la asignatura **Arquitectura Aplicada del Computador**.

## Descripción

Sistema de reconocimiento de locutores (hasta 20) que procesa audio en tiempo real
mediante MFCC + GMM en una PC y transmite el identificador a un microcontrolador
Arduino, el cual lo muestra en displays de 7 segmentos, enciende LEDs indicadores
y emite retroalimentación sonora.

## Tecnologías

- Python 3.10+
- librosa, scikit-learn, sounddevice
- Arduino (UNO/Mega/ESP32)
- Comunicación UART por USB-Serial

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/reconocimiento-voz-locutores.git
cd reconocimiento-voz-locutores

# Crear el entorno virtual
python -m venv venv

# Activarlo (Windows)
.\venv\Scripts\Activate.ps1

# Activarlo (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Estructura del proyecto

```
reconocimiento_voz/
├── src/              Código fuente
├── grabaciones/      Muestras de audio por locutor
├── modelos/          Modelos GMM entrenados
├── pruebas/          Muestras de validación
├── resultados/       Matrices de confusión y logs
└── docs/             Documentación
```

## Estado del desarrollo

- [x] Etapa 0: Preparación del entorno
- [ ] Etapa 1: Captura de audio
- [ ] Etapa 2: Extracción MFCC
- [ ] Etapa 3: Entrenamiento GMM
- [ ] Etapa 4: Identificación de locutor
- [ ] Etapa 5: Funcionamiento en tiempo real
- [ ] Etapa 6: Comunicación serial con Arduino

## Autor

[Tu nombre] — [Tu universidad]
```

**Paso 2 — Crear el script `src/hola_mundo.py`** para verificar que todas las librerías cargan correctamente:

```python
"""
Script de verificación del entorno.
Comprueba que todas las dependencias del proyecto se importan correctamente.
"""

print("Verificando librerías del proyecto...\n")

try:
    import numpy as np
    print(f"[OK] numpy        versión {np.__version__}")
except ImportError as e:
    print(f"[ERROR] numpy: {e}")

try:
    import scipy
    print(f"[OK] scipy        versión {scipy.__version__}")
except ImportError as e:
    print(f"[ERROR] scipy: {e}")

try:
    import sounddevice as sd
    print(f"[OK] sounddevice  versión {sd.__version__}")
except ImportError as e:
    print(f"[ERROR] sounddevice: {e}")

try:
    import soundfile as sf
    print(f"[OK] soundfile    versión {sf.__version__}")
except ImportError as e:
    print(f"[ERROR] soundfile: {e}")

try:
    import librosa
    print(f"[OK] librosa      versión {librosa.__version__}")
except ImportError as e:
    print(f"[ERROR] librosa: {e}")

try:
    import sklearn
    print(f"[OK] scikit-learn versión {sklearn.__version__}")
except ImportError as e:
    print(f"[ERROR] sklearn: {e}")

try:
    import matplotlib
    print(f"[OK] matplotlib   versión {matplotlib.__version__}")
except ImportError as e:
    print(f"[ERROR] matplotlib: {e}")

try:
    import serial
    print(f"[OK] pyserial     versión {serial.__version__}")
except ImportError as e:
    print(f"[ERROR] pyserial: {e}")

print("\nEntorno verificado correctamente. Listo para iniciar la Etapa 1.")
```

**Paso 3 — Ejecutar el script de verificación:**

```bash
python src/hola_mundo.py
```

**Resultado esperado:** todas las librerías aparecen con `[OK]` y su versión, sin ningún `[ERROR]`.

**Paso 4 — Hacer commit del trabajo y subirlo:**

```bash
git add .
git commit -m "Etapa 0 completada: README, script de verificación y estructura final"
git push
```

**Validación de la tarea:** el script muestra todas las librerías con OK, y los cambios se ven reflejados en GitHub.

---

## 6. Entregables de la Etapa 0

Al finalizar esta etapa se debe contar con:

- Repositorio en GitHub con la estructura del proyecto.
- Entorno virtual `venv/` configurado localmente.
- Archivo `requirements.txt` con las 8 dependencias.
- Archivo `.gitignore` correctamente configurado.
- Archivo `README.md` con descripción, instalación y estado del proyecto.
- Script `src/hola_mundo.py` que verifica todas las dependencias.
- Script `src/verificar_audio.py` que lista dispositivos de audio.
- Micrófono detectado y funcional.

---

## 7. Checklist de validación de la etapa

Antes de pasar a la Etapa 1, verificar:

- [ ] `python --version` devuelve 3.10 o superior.
- [ ] El entorno virtual se activa correctamente y el prompt muestra `(venv)`.
- [ ] `pip list` muestra las 8 librerías instaladas.
- [ ] `python src/hola_mundo.py` no devuelve ningún error.
- [ ] `python src/verificar_audio.py` muestra el micrófono en la lista.
- [ ] El repositorio existe en GitHub y contiene todos los archivos del proyecto.
- [ ] El archivo `.gitignore` excluye correctamente `venv/`, audios y modelos.
- [ ] El README está completo y se ve correctamente formateado en GitHub.

---

## 8. Problemas comunes y soluciones

| Problema | Causa probable | Solución |
|---|---|---|
| `python` no se reconoce como comando | No está en el PATH | Reinstalar Python marcando "Add to PATH" o usar `py` en Windows |
| Error al activar `venv` en PowerShell | Política de ejecución restrictiva | Ejecutar `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `sounddevice` falla al instalar en Linux | Falta `portaudio` | Ejecutar `sudo apt-get install libportaudio2` |
| `librosa` tarda mucho en instalar | Depende de `numba` y `llvmlite` | Es normal, esperar a que termine (puede tomar 5-10 minutos) |
| El micrófono no aparece en `sd.query_devices()` | Permisos del sistema operativo | Revisar permisos de privacidad de micrófono en el SO |
| `git push` pide credenciales constantemente | Falta configuración de credenciales | Usar token personal de GitHub o configurar SSH keys |

---

## 9. Próximo paso

Una vez completados todos los puntos del checklist, se puede iniciar la **Etapa 1 — Captura y almacenamiento de audio**, cuyo plan de implementación se desarrollará en un documento aparte.

---

*Documento generado para el proyecto de Arquitectura Aplicada del Computador.*
