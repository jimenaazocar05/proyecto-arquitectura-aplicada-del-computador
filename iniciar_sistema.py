"""
Punto de entrada del sistema completo.
Arranca el servidor web y el bucle de identificación en tiempo real.
"""

import threading
from frontend.servidor_web import iniciar_servidor
from src.tiempo_real import SistemaTiempoReal

if __name__ == "__main__":
    thread_web = threading.Thread(target=iniciar_servidor, daemon=True)
    thread_web.start()

    sistema = SistemaTiempoReal()
    try:
        sistema.iniciar()
    except KeyboardInterrupt:
        print("\nSistema detenido.")
