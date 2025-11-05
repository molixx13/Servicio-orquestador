"""
Servidor RPC unificado del Inventario (persistente)
"""

import os
import socket
import threading
import socketserver
from http.server import HTTPServer, SimpleHTTPRequestHandler
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from functools import partial
from inventario_service import InventarioService

# Configuración
HOST_IP = str(socket.gethostbyname(socket.gethostname()))
RPC_PORT = 8010
WEB_PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def ejecutar_servidor_web():
    """Inicia servidor web para docs sin cambiar cwd."""
    os.makedirs(DOCS_DIR, exist_ok=True)

    handler = partial(SimpleHTTPRequestHandler, directory=DOCS_DIR)
    httpd = HTTPServer(("0.0.0.0", WEB_PORT), handler)

    def run():
        print(f"\n🌐 Servidor web iniciado en http://{HOST_IP}:{WEB_PORT}")
        print("   Documentación disponible en:")
        print("      • main.html")
        print("      • server.html")
        print("      • services.html\n")
        httpd.serve_forever()

    t = threading.Thread(target=run, daemon=True)
    t.start()


def start_server():
    """Inicia servidor XML-RPC con registro de métodos y persistencia al cerrar."""
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ("/rpc",)

    class ThreadedXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
        pass

    inventario_service = InventarioService()

    server = ThreadedXMLRPCServer((HOST_IP, RPC_PORT),
                                  requestHandler=RequestHandler,
                                  allow_none=True,
                                  logRequests=True)

    # Registrar métodos
    server.register_function(inventario_service.cargarProductos, "cargarProductos")
    server.register_function(inventario_service.actualizarInventario, "actualizarInventario")
    server.register_function(inventario_service.cargarRequerimientosProductos, "cargarRequerimientosProductos")
    server.register_function(inventario_service.obtenerProducto, "obtenerProducto")
    server.register_function(inventario_service.listarProductos, "listarProductos")
    server.register_function(inventario_service.listarRequerimientos, "listarRequerimientos")
    server.register_function(inventario_service.estadisticasInventario, "estadisticasInventario")
    server.register_function(inventario_service.healthCheck, "healthCheck")

    server.register_introspection_functions()

    # Banner
    print("=" * 70)
    print("🚀 SERVIDOR INVENTARIO INICIADO")
    print("=" * 70)
    print(f"📍 IP: {HOST_IP}")
    print(f"🔌 Puerto RPC: {RPC_PORT}")
    print(f"🌐 Endpoint: http://{HOST_IP}:{RPC_PORT}/rpc")
    print(f"📡 Protocolo: XML-RPC | JSON")
    print("=" * 70)
    print("\n⏳ Esperando llamadas RPC...\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor RPC de Inventario...")
        inventario_service.guardar_datos()
        server.server_close()
        print("✅ Inventario guardado correctamente antes de salir.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        inventario_service.guardar_datos()
        server.server_close()


if __name__ == "__main__":
    print("Iniciando servidor de inventario persistente...")
    ejecutar_servidor_web()
    start_server()
