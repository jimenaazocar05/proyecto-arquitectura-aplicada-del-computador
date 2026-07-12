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
- [x] Etapa 1: Captura de audio
- [x] Etapa 2: Extracción MFCC
- [x] Etapa 3: Entrenamiento GMM
- [ ] Etapa 4: Identificación de locutor
- [ ] Etapa 5: Funcionamiento en tiempo real
- [ ] Etapa 6: Comunicación serial con Arduino

