"""
Detector de enunciados en tiempo real.
Escucha el micrófono continuamente y devuelve fragmentos con voz completa.
"""

import numpy as np
import sounddevice as sd
from collections import deque
from typing import Callable

from src.config import (
    FRECUENCIA_MUESTREO,
    FRAME_VAD_MS,
    FRAME_VAD_MUESTRAS,
    DURACION_MINIMA_VOZ_MS,
    SILENCIO_FIN_ENUNCIADO_MS,
    BUFFER_PREVIO_MS,
    DURACION_MAXIMA_ENUNCIADO_S,
    DURACION_MINIMA_ENUNCIADO_S,
    DISPOSITIVO_ENTRADA,
)
from src.vad import es_voz


class DetectorEnunciados:
    """
    Escucha el micrófono continuamente y detecta enunciados completos.

    Un enunciado se considera:
    - Iniciado: cuando hay >= DURACION_MINIMA_VOZ_MS de voz consecutiva.
    - Terminado: cuando hay >= SILENCIO_FIN_ENUNCIADO_MS de silencio tras el último frame con voz.

    Al detectar un enunciado completo, llama al callback con el audio.
    """

    def __init__(self, callback: Callable[[np.ndarray], None]):
        self.callback = callback

        # Frames requeridos para las decisiones
        self._frames_min_voz = DURACION_MINIMA_VOZ_MS // FRAME_VAD_MS
        self._frames_silencio_fin = SILENCIO_FIN_ENUNCIADO_MS // FRAME_VAD_MS
        self._frames_buffer_previo = BUFFER_PREVIO_MS // FRAME_VAD_MS
        self._frames_max_enunciado = int(DURACION_MAXIMA_ENUNCIADO_S * 1000) // FRAME_VAD_MS

        # Estado del detector
        self._buffer_previo = deque(maxlen=self._frames_buffer_previo)
        self._enunciado_actual = []
        self._frames_voz_consecutivos = 0
        self._frames_silencio_consecutivos = 0
        self._grabando_enunciado = False

    def _procesar_frame(self, frame: np.ndarray):
        """Procesa un frame nuevo y actualiza el estado del detector."""
        con_voz = es_voz(frame)

        if not self._grabando_enunciado:
            # Estado: esperando inicio de enunciado
            self._buffer_previo.append(frame)

            if con_voz:
                self._frames_voz_consecutivos += 1
                if self._frames_voz_consecutivos >= self._frames_min_voz:
                    # ¡Enunciado iniciado! Incluir buffer previo.
                    self._grabando_enunciado = True
                    self._enunciado_actual = list(self._buffer_previo)
                    self._frames_silencio_consecutivos = 0
            else:
                self._frames_voz_consecutivos = 0

        else:
            # Estado: grabando enunciado
            self._enunciado_actual.append(frame)

            if con_voz:
                self._frames_silencio_consecutivos = 0
            else:
                self._frames_silencio_consecutivos += 1

            # ¿Fin por silencio?
            fin_por_silencio = self._frames_silencio_consecutivos >= self._frames_silencio_fin

            # ¿Fin por duración máxima?
            fin_por_duracion = len(self._enunciado_actual) >= self._frames_max_enunciado

            if fin_por_silencio or fin_por_duracion:
                self._finalizar_enunciado()

    def _finalizar_enunciado(self):
        """Cierra el enunciado actual y llama al callback si es válido."""
        audio_enunciado = np.concatenate(self._enunciado_actual)
        duracion_s = len(audio_enunciado) / FRECUENCIA_MUESTREO

        if duracion_s >= DURACION_MINIMA_ENUNCIADO_S:
            self.callback(audio_enunciado)
        else:
            print(f"  [Descartado: enunciado muy corto ({duracion_s:.2f}s)]")

        # Reset
        self._enunciado_actual = []
        self._frames_voz_consecutivos = 0
        self._frames_silencio_consecutivos = 0
        self._grabando_enunciado = False
        self._buffer_previo.clear()

    def _stream_callback(self, indata, frames, time_info, status):
        """Callback llamado por sounddevice con cada bloque de audio."""
        if status:
            print(f"  [Aviso stream: {status}]")

        # indata tiene shape (frames, canales). Aplanar a mono si es necesario.
        frame = indata[:, 0] if indata.ndim > 1 else indata
        frame = frame.astype(np.float32).flatten()
        self._procesar_frame(frame)

    def escuchar(self):
        """Inicia el bucle de escucha. Bloqueante hasta Ctrl+C."""
        print("Escuchando... (Ctrl+C para detener)")

        with sd.InputStream(
            samplerate=FRECUENCIA_MUESTREO,
            channels=1,
            dtype="float32",
            blocksize=FRAME_VAD_MUESTRAS,
            device=DISPOSITIVO_ENTRADA,
            callback=self._stream_callback,
        ):
            try:
                while True:
                    sd.sleep(100)   # Yield al event loop
            except KeyboardInterrupt:
                print("\nEscucha detenida por el usuario.")


# ============================================================
# PRUEBA RÁPIDA DEL MÓDULO
# ============================================================
if __name__ == "__main__":
    """
    Prueba: cada vez que se detecte un enunciado, muestra su duración y RMS.
    """

    def cb(audio):
        duracion = len(audio) / FRECUENCIA_MUESTREO
        rms = float(np.sqrt(np.mean(audio ** 2)))
        print(f"  Enunciado detectado: {duracion:.2f} s, RMS = {rms:.4f}")

    detector = DetectorEnunciados(callback=cb)
    detector.escuchar()
