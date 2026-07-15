"""
Módulo de identificación de locutores.
Carga los modelos entrenados y decide a quién pertenece una nueva grabación.
"""

import sys
import numpy as np
from pathlib import Path
from dataclasses import dataclass

from src.config import (
    UMBRAL_DESCONOCIDO,
    ID_DESCONOCIDO,
    USAR_LLR,
)
from src.feature_extractor import extraer_features
from src.modelos_io import (
    cargar_modelo_locutor,
    cargar_modelo,
    ruta_modelo_ubm,
    listar_modelos_disponibles,
)


@dataclass
class ResultadoIdentificacion:
    """Estructura que empaqueta el resultado de una identificación."""
    id_predicho: int          # 0 si desconocido, 1-20 si registrado
    llr_maximo: float         # LLR del mejor candidato
    id_mejor_candidato: int   # ID del mejor candidato aunque no supere el umbral
    scores: dict              # {id_locutor: llr}
    es_desconocido: bool

    def __repr__(self):
        etiqueta = "DESCONOCIDO" if self.es_desconocido else f"locutor {self.id_predicho:02d}"
        return (
            f"ResultadoIdentificacion({etiqueta}, "
            f"llr_max={self.llr_maximo:.3f}, "
            f"mejor_candidato={self.id_mejor_candidato:02d})"
        )


class Identificador:
    """
    Identificador de locutor.
    Carga los modelos una sola vez y expone la función identificar().
    """

    def __init__(self, umbral: float = None, verbose: bool = False):
        self.umbral = umbral if umbral is not None else UMBRAL_DESCONOCIDO
        self.verbose = verbose
        self.modelos = {}
        self.ubm = None
        self._cargar_todos()

    def _cargar_todos(self):
        """Carga en memoria los modelos de todos los locutores registrados y el UBM."""
        ids = listar_modelos_disponibles()
        if not ids:
            raise RuntimeError(
                "No hay modelos entrenados. Ejecuta primero `python -m src.entrenar_todos`."
            )

        for id_locutor in ids:
            self.modelos[id_locutor] = cargar_modelo_locutor(id_locutor)

        # Cargar UBM si existe
        ruta_ubm = ruta_modelo_ubm()
        if ruta_ubm.exists():
            self.ubm = cargar_modelo(ruta_ubm)
        elif USAR_LLR:
            raise RuntimeError(
                "USAR_LLR=True requiere UBM entrenado. "
                "Ejecuta `python -m src.entrenar_todos`."
            )

        if self.verbose:
            print(f"Identificador cargado: {len(self.modelos)} locutores + "
                  f"{'UBM' if self.ubm else 'sin UBM'}")

    def _calcular_scores(self, features: np.ndarray) -> dict:
        """
        Calcula el score de cada modelo sobre las features dadas.
        Si USAR_LLR está activo, aplica normalización por UBM.
        """
        scores = {}

        if USAR_LLR and self.ubm is not None:
            score_ubm = self.ubm.score(features)
            for id_locutor, modelo in self.modelos.items():
                scores[id_locutor] = modelo.score(features) - score_ubm
        else:
            for id_locutor, modelo in self.modelos.items():
                scores[id_locutor] = modelo.score(features)

        return scores

    def identificar(self, ruta_wav) -> ResultadoIdentificacion:
        """
        Identifica al locutor de una grabación.

        Parámetros
        ----------
        ruta_wav : Path o str
            Ruta al archivo WAV a identificar.

        Retorna
        -------
        ResultadoIdentificacion
        """
        features = extraer_features(Path(ruta_wav))
        scores = self._calcular_scores(features)

        # Ganador
        id_mejor = max(scores, key=scores.get)
        llr_max = scores[id_mejor]

        # Decisión final según umbral
        es_desconocido = llr_max < self.umbral
        id_predicho = ID_DESCONOCIDO if es_desconocido else id_mejor

        return ResultadoIdentificacion(
            id_predicho=id_predicho,
            llr_maximo=llr_max,
            id_mejor_candidato=id_mejor,
            scores=scores,
            es_desconocido=es_desconocido,
        )

    def identificar_audio(self, audio: np.ndarray) -> ResultadoIdentificacion:
        """
        Identifica al locutor a partir de un array de audio en memoria.
        Usa el mismo pipeline que identificar() pero sin pasar por archivo.

        Parámetros
        ----------
        audio : np.ndarray
            Array 1D de audio a la frecuencia de muestreo del proyecto.

        Retorna
        -------
        ResultadoIdentificacion
        """
        from src.preprocesamiento import preprocesar
        from src.feature_extractor import (
            extraer_mfcc_basico, calcular_deltas, normalizar_cmn,
        )
        from src.config import USAR_DELTAS, USAR_DELTA_DELTAS, APLICAR_CMN

        # Pipeline igual al de la Etapa 2, pero sobre array en memoria
        audio_proc = preprocesar(audio)
        mfcc = extraer_mfcc_basico(audio_proc)
        features = mfcc

        if USAR_DELTAS:
            features = np.concatenate([features, calcular_deltas(mfcc)], axis=1)

        if USAR_DELTA_DELTAS:
            from src.feature_extractor import calcular_delta_deltas
            features = np.concatenate([features, calcular_delta_deltas(mfcc)], axis=1)

        if APLICAR_CMN:
            features = normalizar_cmn(features)

        # Reutilizar la lógica existente de scoring y decisión
        scores = self._calcular_scores(features)
        id_mejor = max(scores, key=scores.get)
        llr_max = scores[id_mejor]

        es_desconocido = llr_max < self.umbral
        id_predicho = ID_DESCONOCIDO if es_desconocido else id_mejor

        return ResultadoIdentificacion(
            id_predicho=id_predicho,
            llr_maximo=llr_max,
            id_mejor_candidato=id_mejor,
            scores=scores,
            es_desconocido=es_desconocido,
        )


# ============================================================
# INTERFAZ DE LÍNEA DE COMANDOS
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Identificar locutor de un archivo WAV.")
    parser.add_argument("archivo", type=str, help="Ruta al archivo WAV.")
    parser.add_argument("--umbral", type=float, default=None,
                        help="Umbral de LLR para aceptar identificación.")
    args = parser.parse_args()

    ruta = Path(args.archivo)
    if not ruta.exists():
        print(f"El archivo no existe: {ruta}")
        sys.exit(1)

    identificador = Identificador(umbral=args.umbral, verbose=True)
    print(f"\nIdentificando: {ruta.name}\n")

    resultado = identificador.identificar(ruta)

    print("--- SCORES POR LOCUTOR (LLR) ---")
    for id_locutor, score in sorted(resultado.scores.items(), key=lambda x: -x[1]):
        marca = " ** ganador" if id_locutor == resultado.id_mejor_candidato else ""
        print(f"  Locutor {id_locutor:02d}: {score:+.3f}{marca}")

    print(f"\nUmbral configurado: {identificador.umbral:.3f}")
    print(f"LLR del ganador: {resultado.llr_maximo:.3f}")

    if resultado.es_desconocido:
        print(f"\n*** DECISIÓN: LOCUTOR DESCONOCIDO (ID = 0) ***")
        print(f"    Mejor candidato habría sido: locutor {resultado.id_mejor_candidato:02d}")
    else:
        print(f"\n*** DECISIÓN: LOCUTOR {resultado.id_predicho:02d} ***")
