"""
Bucle principal del sistema en tiempo real.
Escucha el micrófono, detecta enunciados, identifica y muestra el resultado.
"""

import time
import numpy as np

from src.detector_enunciados import DetectorEnunciados
from src.identifier import Identificador
from src.config import FRECUENCIA_MUESTREO, ID_DESCONOCIDO


class SistemaTiempoReal:
    """
    Orquesta el sistema completo: detector + identificador.
    """

    def __init__(self):
        print("Cargando identificador y modelos...")
        self.identificador = Identificador(verbose=False)
        self.detector = DetectorEnunciados(callback=self._al_detectar_enunciado)
        self.contador = 0
        print(f"  {len(self.identificador.modelos)} locutores cargados.")
        print(f"  Umbral de decisión: {self.identificador.umbral:.3f}")
        print()

    def _al_detectar_enunciado(self, audio: np.ndarray):
        """Callback llamado cada vez que el detector encuentra un enunciado."""
        self.contador += 1
        duracion = len(audio) / FRECUENCIA_MUESTREO

        # Medir tiempo de procesamiento
        t0 = time.time()
        resultado = self.identificador.identificar_audio(audio)
        t_proceso = time.time() - t0

        # Preparar mensaje
        if resultado.es_desconocido:
            etiqueta = "DESCONOCIDO"
            id_output = 0
            color = "\033[93m"  # Amarillo
        else:
            etiqueta = f"LOCUTOR {resultado.id_predicho:02d}"
            id_output = resultado.id_predicho
            color = "\033[92m"  # Verde

        reset = "\033[0m"

        # Salida en consola
        print(
            f"[Enunciado #{self.contador:03d}] "
            f"duración={duracion:.2f}s | "
            f"procesado en {t_proceso*1000:.0f}ms | "
            f"LLR={resultado.llr_maximo:+.3f}"
        )
        print(f"{color}  →  ID = {id_output:02d}  ({etiqueta}){reset}")
        print()

    def iniciar(self):
        """Arranca el bucle de escucha en tiempo real."""
        print("=" * 60)
        print("  SISTEMA DE IDENTIFICACIÓN DE VOZ EN TIEMPO REAL")
        print("=" * 60)
        print()
        print("Habla al micrófono. El sistema identificará al locutor.")
        print("Pulsa Ctrl+C para detener.")
        print()

        self.detector.escuchar()


if __name__ == "__main__":
    sistema = SistemaTiempoReal()
    sistema.iniciar()
