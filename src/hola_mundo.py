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
