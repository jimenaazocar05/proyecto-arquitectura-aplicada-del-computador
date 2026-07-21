"""
Bucle principal del sistema en tiempo real.
Escucha el micrófono, detecta enunciados, identifica y muestra el resultado.
"""

import json
import time
import urllib.request
import numpy as np

from src.detector_enunciados import DetectorEnunciados
from src.identifier import Identificador
from src.config import (
    FRECUENCIA_MUESTREO,
    ID_DESCONOCIDO,
    NOMBRES_LOCUTORES,
    HOST_WEB,
    PUERTO_WEB,
)
from src.serial_comm import ComunicacionArduino


def notificar_web(id_locutor: int, nombre: str):
    try:
        data = json.dumps({"id": id_locutor, "nombre": nombre}).encode()
        req = urllib.request.Request(
            f"http://{HOST_WEB}:{PUERTO_WEB}/detectar",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=0.5)
    except Exception:
        pass


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

        # Conexión al Arduino
        print("\nConectando al Arduino...")
        self.arduino = ComunicacionArduino()
        if self.arduino.conectar():
            print("  Arduino conectado.")
        else:
            print("  AVISO: Arduino no disponible. El sistema funcionará solo en consola.")

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

        print(
            f"[Enunciado #{self.contador:03d}] "
            f"duración={duracion:.2f}s | "
            f"procesado en {t_proceso*1000:.0f}ms | "
            f"LLR={resultado.llr_maximo:+.3f}"
        )
        print(f"{color}  →  ID = {id_output:02d}  ({etiqueta}){reset}")

        # Notificar al frontend web
        nombre = NOMBRES_LOCUTORES.get(id_output, f"Locutor {id_output:02d}")
        notificar_web(id_output, nombre)

        # Enviar al Arduino
        if self.arduino.esta_conectado():
            exito = self.arduino.enviar_id(id_output)
            if not exito:
                print(f"  [AVISO] No se pudo enviar al Arduino, se intentará reconectar.")

        print()

    def iniciar(self):
        """Arranca el bucle de escucha en tiempo real."""
        print("=" * 60)
        print("  SISTEMA DE IDENTIFICACIÓN DE VOZ EN TIEMPO REAL")
        print("=" * 60)
        print()
        print("Habla al micrófono. El sistema identificará al locutor")
        print("y mostrará el resultado en los displays físicos.")
        print("Pulsa Ctrl+C para detener.")
        print()

        try:
            self.detector.escuchar()
        finally:
            self.arduino.desconectar()


if __name__ == "__main__":
    sistema = SistemaTiempoReal()
    sistema.iniciar()
