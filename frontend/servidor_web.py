"""
Servidor web con SSE para mostrar en tiempo real el locutor identificado.
Usa solo la biblioteca estándar de Python (sin Flask ni dependencias externas).
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
from pathlib import Path

from src.config import NOMBRES_LOCUTORES, HOST_WEB, PUERTO_WEB

RAIZ = Path(__file__).parent

ultima_deteccion = {
    "id": 0,
    "nombre": NOMBRES_LOCUTORES[0],
    "timestamp": time.time(),
    "es_desconocido": True,
}
lock = threading.Lock()
contador_eventos = 0


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _enviar_json(self, datos, codigo=200):
        body = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        ruta = urlparse(self.path).path

        if ruta == "/":
            html = RAIZ / "index.html"
            if html.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        elif ruta == "/eventos":
            self._manejar_sse()
        elif ruta == "/api/ultimo":
            with lock:
                self._enviar_json(ultima_deteccion)
        else:
            self.send_error(404)

    def do_POST(self):
        ruta = urlparse(self.path).path

        if ruta == "/detectar":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                id_recibido = body.get("id", 0)
                nombre = body.get("nombre", NOMBRES_LOCUTORES.get(id_recibido, f"Locutor {id_recibido:02d}"))

                with lock:
                    global contador_eventos
                    contador_eventos += 1
                    ultima_deteccion["id"] = id_recibido
                    ultima_deteccion["nombre"] = nombre
                    ultima_deteccion["es_desconocido"] = id_recibido == 0
                    ultima_deteccion["timestamp"] = time.time()

                self._enviar_json({"ok": True})
            except Exception as e:
                self._enviar_json({"ok": False, "error": str(e)}, 400)
        else:
            self.send_error(404)

    def _manejar_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        ultimo_contador = -1
        try:
            while True:
                with lock:
                    actual = contador_eventos
                    if actual != ultimo_contador:
                        ultimo_contador = actual
                        datos = dict(ultima_deteccion)
                    else:
                        datos = None

                if datos:
                    msg = f"data: {json.dumps(datos)}\n\n"
                    self.wfile.write(msg.encode())
                    self.wfile.flush()

                time.sleep(0.2)
        except (BrokenPipeError, ConnectionResetError):
            pass


def iniciar_servidor(host: str = None, puerto: int = None):
    host = host or HOST_WEB
    puerto = puerto or PUERTO_WEB
    servidor = ThreadedHTTPServer((host, puerto), Manejador)
    print(f"[Web] Servidor en http://{host}:{puerto}")
    print(f"[Web] Abre http://localhost:{puerto} en el navegador")
    servidor.serve_forever()


if __name__ == "__main__":
    iniciar_servidor()
