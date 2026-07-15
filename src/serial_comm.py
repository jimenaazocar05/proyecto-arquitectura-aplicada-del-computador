"""
Módulo de comunicación serial con el microcontrolador.
Gestiona el envío de tramas con checksum y la reconexión automática.
"""

import time
import serial
from serial.serialutil import SerialException
from typing import Optional

from src.config import (
    PUERTO_SERIAL,
    BAUDIOS_SERIAL,
    TIMEOUT_SERIAL_S,
    DELAY_RECONEXION_S,
    CABECERA_TRAMA,
    DEBUG_SERIAL,
)


class ComunicacionArduino:
    """
    Cliente serial hacia el Arduino con reconexión automática.
    """

    def __init__(self, puerto: str = None, baudios: int = None):
        self.puerto_nombre = puerto or PUERTO_SERIAL
        self.baudios = baudios or BAUDIOS_SERIAL
        self.puerto: Optional[serial.Serial] = None

    def conectar(self) -> bool:
        """
        Intenta abrir el puerto serial.
        Retorna True si se establece la conexión, False en caso contrario.
        """
        try:
            self.puerto = serial.Serial(
                port=self.puerto_nombre,
                baudrate=self.baudios,
                timeout=TIMEOUT_SERIAL_S,
            )
            time.sleep(2)   # El Arduino se reinicia al abrir el puerto
            if DEBUG_SERIAL:
                print(f"[Serial] Conectado a {self.puerto_nombre} @ {self.baudios} bps")
            return True
        except SerialException as e:
            if DEBUG_SERIAL:
                print(f"[Serial] Error al conectar: {e}")
            self.puerto = None
            return False

    def desconectar(self):
        """Cierra el puerto serial si está abierto."""
        if self.puerto and self.puerto.is_open:
            self.puerto.close()
            if DEBUG_SERIAL:
                print("[Serial] Desconectado.")
        self.puerto = None

    def esta_conectado(self) -> bool:
        return self.puerto is not None and self.puerto.is_open

    def enviar_id(self, id_locutor: int) -> bool:
        """
        Envía un ID al Arduino en formato de trama de 3 bytes.

        Trama: [cabecera=0xAA, id, checksum=cabecera XOR id]

        Retorna True si el envío fue exitoso.
        """
        if not (0 <= id_locutor <= 20):
            raise ValueError(f"ID debe estar entre 0 y 20, recibido: {id_locutor}")

        if not self.esta_conectado():
            if not self.conectar():
                return False

        checksum = CABECERA_TRAMA ^ id_locutor
        trama = bytes([CABECERA_TRAMA, id_locutor, checksum])

        try:
            self.puerto.write(trama)
            if DEBUG_SERIAL:
                print(f"[Serial] Enviado: {' '.join(f'{b:02X}' for b in trama)} "
                      f"(ID={id_locutor})")
            return True
        except SerialException as e:
            if DEBUG_SERIAL:
                print(f"[Serial] Error al enviar: {e}. Reintentando en {DELAY_RECONEXION_S}s...")
            self.desconectar()
            time.sleep(DELAY_RECONEXION_S)
            return False

    def leer_respuesta(self, max_espera_ms: int = 500) -> str:
        """
        Lee la respuesta ASCII del Arduino durante max_espera_ms milisegundos.
        Útil para depuración.
        """
        if not self.esta_conectado():
            return ""

        buffer = b""
        deadline = time.time() + max_espera_ms / 1000
        while time.time() < deadline:
            n = self.puerto.in_waiting
            if n > 0:
                buffer += self.puerto.read(n)
            else:
                time.sleep(0.01)
        return buffer.decode("utf-8", errors="replace")


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enviar un ID al Arduino por serial.")
    parser.add_argument("id", type=int, help="ID a enviar (0-20).")
    parser.add_argument("--puerto", type=str, default=None, help="Puerto serial.")
    args = parser.parse_args()

    arduino = ComunicacionArduino(puerto=args.puerto)
    if arduino.conectar():
        arduino.enviar_id(args.id)
        respuesta = arduino.leer_respuesta(800)
        if respuesta.strip():
            print(f"[Arduino] {respuesta}")
        arduino.desconectar()
    else:
        print("No se pudo conectar al Arduino.")
