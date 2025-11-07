"""
Servidor de Documentación - Componente Tienda
Autor: Molixx13
Fecha: 2025-11-06
Descripción:
---------------
Servidor HTTP que muestra la documentación técnica del componente TIENDA
del sistema distribuido de Compras/Ventas.

Puerto: 8082
Accesible desde cualquier navegador en la red local SIN autenticación.
Basado en el estilo pydocs utilizado en el resto del sistema.
"""

import http.server
import socketserver
import socket

PUERTO_DOCUMENTACION = 8094  # Puerto dedicado a Tienda

# ===========================================================
# Funciones de utilidad
# ===========================================================
def obtener_ip_local():
    """Obtiene la dirección IP local del equipo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def crear_pagina_principal():
    """Crea la documentación HTML principal para el componente Tienda."""
    ip = obtener_ip_local()

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Documentación Técnica - Componente Tienda</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        background: linear-gradient(180deg, #f4f6fa 0%, #e9ecf5 100%);
        color: #222;
    }}
    .container {{
        max-width: 1200px;
        margin: 40px auto;
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        overflow: hidden;
        padding-bottom: 30px;
    }}
    .header {{
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        color: white;
        padding: 30px;
        text-align: center;
    }}
    .header h1 {{
        margin-bottom: 10px;
    }}
    h2 {{
        border-left: 5px solid #4e54c8;
        padding-left: 10px;
        color: #4e54c8;
        margin-top: 35px;
    }}
    p, li {{
        line-height: 1.6;
    }}
    pre {{
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 10px;
        border-radius: 8px;
        overflow-x: auto;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin-top: 10px;
    }}
    th, td {{
        border-bottom: 1px solid #ddd;
        padding: 10px;
        text-align: left;
    }}
    th {{
        background: #4e54c8;
        color: white;
    }}
    .section {{
        padding: 20px 40px;
    }}
    .info-bar {{
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        background: #f3f4fb;
        border-bottom: 3px solid #4e54c8;
        padding: 15px 25px;
    }}
    .info-item {{
        background: white;
        border-radius: 8px;
        padding: 10px 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        flex: 1;
        min-width: 220px;
    }}
    .warning {{
        background: #fff8e1;
        border-left: 5px solid #ffc107;
        padding: 10px;
        border-radius: 6px;
        margin-top: 10px;
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛍️ Componente Tienda — Sistema Distribuido de Compras/Ventas</h1>
        <p>Documentación Técnica y Operativa | Autor: Molixx13 — {ip}:{PUERTO_DOCUMENTACION}</p>
    </div>

    <div class="info-bar">
        <div class="info-item"><strong>📍 IP Servidor:</strong> {ip}</div>
        <div class="info-item"><strong>🔌 Puerto:</strong> {PUERTO_DOCUMENTACION}</div>
        <div class="info-item"><strong>🧠 Tipo:</strong> Cliente interactivo (ventas / inventario)</div>
        <div class="info-item"><strong>🌐 Protocolo:</strong> XML-RPC</div>
    </div>

    <div class="section">
        <h2>📘 Resumen Ejecutivo</h2>
        <p>El componente <strong>Tienda</strong> es un cliente interactivo orientado a la operación de ventas dentro del sistema distribuido. Ofrece dos modos principales:</p>
        <ul>
            <li><strong>Modo Compras:</strong> Simula y registra ventas en el sistema, comunicándose con el orquestador (Compras/Ventas).</li>
            <li><strong>Modo Inventario:</strong> Permite gestión administrativa: listar, crear, actualizar productos y consultar estadísticas.</li>
        </ul>
        <p>Implementado en Python, utiliza <code>xmlrpc.client.ServerProxy</code> para la comunicación remota con los servicios Inventario, Compras/Ventas y Transportador.</p>
    </div>

    <div class="section">
        <h2>🎯 Objetivos Funcionales</h2>
        <ul>
            <li>Proveer experiencia de venta en consola, registrando transacciones y coordinando envíos.</li>
            <li>Facilitar gestión de catálogo (cargarProductos, actualizarInventario, estadísticas).</li>
            <li>Operar con tolerancia a fallos, evitando bloqueos ante fallas remotas.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🏗️ Arquitectura y Dependencias RPC</h2>
        <table>
            <tr><th>Servicio</th><th>Propósito</th><th>Endpoint Ejemplo</th></tr>
            <tr><td>Inventario</td><td>Listado y actualización de productos</td><td>http://25.21.199.213:8010/rpc</td></tr>
            <tr><td>Compras/Ventas</td><td>Registro de ventas y compras</td><td>http://192.168.100.233:9000/rpc</td></tr>
            <tr><td>Transportador</td><td>Gestión logística / envíos</td><td>http://25.21.199.213:7000</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>📡 Contrato RPC (Consumo)</h2>
        <p>El componente Tienda invoca métodos remotos mediante XML-RPC. Los datos se envían como parámetros primarios o JSON serializado:</p>

        <pre>
inventario_rpc.listarProductos() → {{
  "total_productos": 3,
  "data": [{{"id":1,"nombre":"Silla","stock":20,"precio":350000}}, ...]
}}

compras_rpc.registrar_venta(cliente, productos, total) → {{
  "status":"ok","id_venta":"VENTA-001","factura":"FACT-..."
}}

transportador_rpc.ordenarTransporte(envio_data_json) → {{
  "status":"ok","tracking_id":"TRK-12345"
}}
        </pre>
    </div>

    <div class="section">
        <h2>🧭 Flujo de Venta (Paso a Paso)</h2>
        <ol>
            <li>Tienda solicita <code>listarProductos()</code> al servicio de Inventario.</li>
            <li>El usuario selecciona producto y cantidad.</li>
            <li>Tienda valida stock localmente.</li>
            <li>Calcula total y llama a <code>registrar_venta()</code> en Compras/Ventas.</li>
            <li>Recibe confirmación o factura.</li>
            <li>Solicita transporte (opcional) llamando a <code>ordenarTransporte()</code>.</li>
            <li>Muestra resultado final en consola.</li>
        </ol>
    </div>

    <div class="section">
        <h2>🧩 Validaciones y Manejo de Errores</h2>
        <ul>
            <li>Verifica que los valores de stock y cantidad sean válidos (int > 0).</li>
            <li>Controla errores de conexión y caídas RPC.</li>
            <li>Notifica al usuario sin interrumpir la sesión.</li>
        </ul>

        <div class="warning">
            <strong>Ejemplo: Transporte con timeout</strong>
            <pre>
from xmlrpc.client import ServerProxy, Transport
class TimeoutTransport(Transport):
    def __init__(self, timeout=8):
        super().__init__()
        self.timeout = timeout
    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

proxy = ServerProxy('http://IP:9000/rpc', transport=TimeoutTransport(8), allow_none=True)
            </pre>
        </div>
    </div>

    <div class="section">
        <h2>🧪 Pruebas y QA</h2>
        <ul>
            <li><strong>Unitarias:</strong> Mock de ServerProxy para validar flujo de venta y manejo de errores.</li>
            <li><strong>Integración:</strong> Ejecutar flujo completo Inventario → Venta → Factura → Transporte.</li>
            <li><strong>Validación:</strong> Comprobar decremento de stock y registro de factura en Contabilidad.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🛡️ Seguridad y Despliegue</h2>
        <ul>
            <li>Usar RPC solo en redes LAN seguras.</li>
            <li>Implementar TLS o VPN en entornos productivos.</li>
            <li>Restringir acceso por firewall y no hardcodear IPs.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🚀 Ejemplo Práctico</h2>
        <pre>
import xmlrpc.client, json
compras = xmlrpc.client.ServerProxy('http://192.168.100.233:9000/rpc', allow_none=True)
resp = compras.registrar_venta('Ana', ['Silla x2'], 700000)
print(resp)

transport = xmlrpc.client.ServerProxy('http://25.21.199.213:7000', allow_none=True)
envio = json.dumps({{'cliente':'Ana','producto':'Silla','cantidad':2,'total':700000}})
print(transport.ordenarTransporte(envio))
        </pre>
    </div>

    <div class="section">
        <h2>💡 Mejoras Técnicas Recomendadas</h2>
        <ul>
            <li><strong>Alta:</strong> Implementar transporte RPC con timeout y reintentos.</li>
            <li><strong>Media:</strong> Persistir operaciones locales fallidas y logging estructurado.</li>
            <li><strong>Baja:</strong> Crear interfaz gráfica (GUI/WEB) para ventas y envíos.</li>
        </ul>
    </div>
</div>
</body>
</html>
"""
    return html


# ===========================================================
# Servidor HTTP
# ===========================================================
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(crear_pagina_principal().encode("utf-8"))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        print(f"🌐 [{self.client_address[0]}] {args[0]}")


def iniciar_servidor():
    ip = obtener_ip_local()
    print("="*70)
    print("📚 SERVIDOR DE DOCUMENTACIÓN — TIENDA")
    print("="*70)
    print(f"📍 IP:       {ip}")
    print(f"🔌 Puerto:   {PUERTO_DOCUMENTACION}")
    print(f"🌐 URL:      http://{ip}:{PUERTO_DOCUMENTACION}")
    print("="*70)

    with socketserver.TCPServer(("0.0.0.0", PUERTO_DOCUMENTACION), Handler) as httpd:
        try:
            print("⏳ Servidor en ejecución. Ctrl+C para detener.\n")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario.")


if __name__ == "__main__":
    iniciar_servidor()

