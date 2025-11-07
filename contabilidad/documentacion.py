"""
Servidor de Documentación - Componente Contabilidad
Autor: Molixx13
Fecha: 2025-11-06
Descripción:
---------------
Servidor HTTP que muestra la documentación técnica del componente Contabilidad
del sistema distribuido de Compras/Ventas.

Puerto: 8083
Accesible desde cualquier navegador en la red local SIN autenticación.
"""

import http.server
import socketserver
import socket

PUERTO_DOCUMENTACION = 8090  # Puerto dedicado a Contabilidad

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
    """Crea la documentación HTML principal para el componente Contabilidad."""
    ip = obtener_ip_local()

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Documentación Técnica - Componente Contabilidad</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        background: linear-gradient(180deg, #f8fafc 0%, #eef1f7 100%);
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
        background: linear-gradient(135deg, #2b5876, #4e4376);
        color: white;
        padding: 30px;
        text-align: center;
    }}
    .header h1 {{
        margin-bottom: 10px;
    }}
    h2 {{
        border-left: 5px solid #2b5876;
        padding-left: 10px;
        color: #2b5876;
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
        background: #2b5876;
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
        border-bottom: 3px solid #2b5876;
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
        <h1>🧾 Componente Contabilidad — Sistema Distribuido de Compras/Ventas</h1>
        <p>Servicio asíncrono de facturación e integridad de inventario • Autor: Molixx13 • Actualizado: 2025-11-06</p>
    </div>

    <div class="info-bar">
        <div class="info-item"><strong>📍 IP Servidor:</strong> {ip}</div>
        <div class="info-item"><strong>🔌 Puerto:</strong> {PUERTO_DOCUMENTACION}</div>
        <div class="info-item"><strong>🧠 Tipo:</strong> Servicio RPC asíncrono</div>
        <div class="info-item"><strong>🌐 Protocolo:</strong> XML-RPC / JSON Payload</div>
    </div>

    <div class="section">
        <h2>📘 Resumen Ejecutivo</h2>
        <p>El componente <strong>Contabilidad</strong> es la autoridad única para la generación de facturas y la actualización del inventario. Está diseñado para responder inmediatamente (≤ 2s) y procesar las actualizaciones de inventario de manera <strong>asíncrona</strong> mediante una cola y un <em>worker thread</em>. Esto garantiza alta disponibilidad y consistencia sobre el stock.</p>
    </div>

    <div class="section">
        <h2>🎯 Propósito y Responsabilidades</h2>
        <ul>
            <li>Generar facturas oficiales para ventas (<code>generarFactura</code>).</li>
            <li>Registrar facturas de compras a proveedores (<code>recibirFactura</code>).</li>
            <li>Procesar actualizaciones de inventario en background de forma confiable.</li>
            <li>Mantener numeración de facturas basada en timestamp y asientos contables simples.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🏗️ Arquitectura Interna</h2>
        <p>Contabilidad se ejecuta como servidor <strong>XML-RPC</strong> (acepta <code>/rpc</code> y <code>/RPC2</code>), crea un <code>ServerProxy</code> hacia Inventario y utiliza una <code>Queue</code> (cola) que alimenta un hilo <em>worker daemon</em> (<code>InventarioWorker</code>).</p>

        <table>
            <tr><th>Componente</th><th>Rol</th></tr>
            <tr><td>Server XML-RPC</td><td>Expone métodos <code>generarFactura</code> y <code>recibirFactura</code></td></tr>
            <tr><td>ServidorContabilidad</td><td>Clase principal con lógica de negocio y la cola</td></tr>
            <tr><td>InventarioWorker</td><td>Hilo que procesa tareas asíncronas de inventario</td></tr>
            <tr><td>ServerProxy hacia Inventario</td><td>Cliente RPC para invocar <code>actualizarInventario</code></td></tr>
        </table>
    </div>

    <div class="section">
        <h2>📡 API RPC — Métodos Expuestos</h2>
        <h3><code>generarFactura(json_data: str) → str</code></h3>
        <p>Genera una factura de venta y encola una actualización de inventario.</p>
        <pre>
Entrada:
{{
  "tipo_operacion": "VENTA",
  "nombre_cliente": "Ana",
  "productos": [{{"nombre":"Silla","cantidad":2,"precio_unit":350000}}],
  "total": 700000
}}
Salida:
{{
  "factura_id": "FACT-20251106103045",
  "tipo": "venta",
  "cliente": "Ana",
  "productos": [...],
  "total": 700000,
  "estado": "Aprobada",
  "fecha": "2025-11-06 10:30:45"
}}
        </pre>

        <h3><code>recibirFactura(json_data: str) → str</code></h3>
        <p>Recibe una compra de proveedor y encola incremento de inventario.</p>
        <pre>
Entrada:
{{
  "tipo": "COMPRA",
  "proveedor": "ProveedorXYZ",
  "productos": ["Mesa","Silla"],
  "total": 500000,
  "compra_id": "COMP-20251106102400",
  "fecha": "2025-11-06 10:24:00"
}}
Salida:
{{
  "status": "ok",
  "mensaje": "Compra COMP-20251106102400 registrada correctamente.",
  "asiento": {{
    "tipo":"COMPRA","compra_id":"COMP-...","proveedor":"...","total":500000
  }}
}}
        </pre>
    </div>

    <div class="section">
        <h2>⚙️ Flujo Interno y Comportamiento Temporal</h2>
        <p>Ambos métodos normalizan los datos, encolan una tarea y devuelven respuesta inmediata. El <strong>worker thread</strong> procesa las tareas en segundo plano mediante llamadas a <code>inventarioRPC.actualizarInventario()</code>.</p>

        <pre>
Compras/Ventas ---> generarFactura(json_data) ---> Contabilidad
Contabilidad: encola ("VENTA", payload, FACT-...)
Contabilidad (worker) ---> inventarioRPC.actualizarInventario(payload)
Inventario ---> responde {{"status":"ok"}} o error
Contabilidad ---> loggea resultado
        </pre>
    </div>

    <div class="section">
        <h2>🔧 Detalles del Worker y Robustez</h2>
        <ul>
            <li>Bloqueante con <code>queue.get()</code> hasta recibir tarea.</li>
            <li>Termina al recibir <code>None</code> (parada segura).</li>
            <li>Captura excepciones y marca <code>task_done()</code> en <em>finally</em>.</li>
            <li>No detiene el servicio ante errores.</li>
        </ul>

        <div class="warning">
            <strong>Recomendaciones de robustez:</strong>
            <ul>
                <li>Implementar reintentos con backoff (1s, 2s, 4s).</li>
                <li>Registrar tareas fallidas en DLQ (<code>failed_inventory_updates.json</code>).</li>
                <li>Alertar si DLQ > 50 entradas.</li>
                <li>Exponer métricas: <code>inventory_updates_total</code>, <code>failures</code>, <code>queue_depth</code>.</li>
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>⚠️ Gestión de Errores y Casos Límite</h2>
        <ul>
            <li>Inventario no responde → worker registra fallo; sin reintentos, operación pendiente.</li>
            <li>Payload inválido → validar antes de encolar.</li>
            <li>Excepción en worker → capturar stacktrace y guardar en DLQ.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🗄️ Persistencia y Auditoría</h2>
        <ul>
            <li>Registrar facturas y asientos en base de datos (SQLite/Postgres).</li>
            <li>Controlar estados de tareas: queued, processing, done, failed.</li>
            <li>DLQ con contador y última excepción.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🔒 Seguridad y Despliegue</h2>
        <ul>
            <li>Habilitar TLS (idealmente mTLS).</li>
            <li>Autenticación y autorización por rol (API keys, tokens).</li>
            <li>Restringir acceso mediante firewall / redes privadas.</li>
        </ul>
    </div>

    <div class="section">
        <h2>🚀 Operación: Inicio y Parada Segura</h2>
        <pre>
# Iniciar servidor:
python contabilidadRCP.py

# Parada controlada:
Ctrl + C → se encola 'None' y el worker finaliza tras procesar la tarea actual.
        </pre>
    </div>

    <div class="section">
        <h2>💡 Ejemplos de Payloads</h2>
        <pre>
Venta:
{{
  "tipo_operacion": "VENTA",
  "nombre_cliente": "Carlos Lopez",
  "productos": [{{"nombre":"Sofá 3 puestos","cantidad":1,"precio_unit":1500000}}],
  "total":1500000
}}

Compra:
{{
  "tipo": "COMPRA",
  "proveedor": "Maderera El Roble",
  "productos": ["Madera","Tablones"],
  "total":10000000,
  "compra_id": "COMP-20251106120000",
  "fecha": "2025-11-06 12:00:00"
}}
        </pre>
    </div>

    <div class="section">
        <h2>🧪 Cliente de Prueba (Python)</h2>
        <pre>
import xmlrpc.client, json
CONT_HOST = 'http://REEMPLAZAR_IP:10010/rpc'
proxy = xmlrpc.client.ServerProxy(CONT_HOST, allow_none=True)

# Generar factura
data_venta = {{
    "tipo_operacion":"VENTA",
    "nombre_cliente":"Prueba Cliente",
    "productos":[{{"nombre":"Silla Prueba","cantidad":2,"precio_unit":350000}}],
    "total":700000
}}
print('-> generarFactura:')
print(proxy.generarFactura(json.dumps(data_venta)))

# Enviar factura compra
data_compra = {{
    "tipo":"COMPRA",
    "proveedor":"ProveedorTest",
    "productos":["MesaTest","SillaTest"],
    "total":200000,
    "compra_id":"COMP-PRUEBA-001",
    "fecha":"2025-11-06 12:34:00"
}}
print('\\n-> recibirFactura:')
print(proxy.recibirFactura(json.dumps(data_compra)))
        </pre>
    </div>

    <div class="section">
        <h2>🧩 Pruebas y QA</h2>
        <ul>
            <li>Levantar Inventario (8010), Contabilidad (10010) y Compras/Ventas (9000).</li>
            <li>Registrar venta desde Tienda y verificar factura + actualización de stock.</li>
            <li>Simular fallo de Inventario para validar DLQ.</li>
        </ul>
    </div>

    <div class="section">
        <h2>📈 Roadmap y Mejoras</h2>
        <ul>
            <li>Persistir facturas/asientos en DB y exponer consulta paginada.</li>
            <li>Implementar reintentos + DLQ con reconciliación.</li>
            <li>Agregar autenticación mTLS y tokens internos.</li>
            <li>Exponer métricas Prometheus y logs JSON estructurados.</li>
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
    print("📚 SERVIDOR DE DOCUMENTACIÓN — CONTABILIDAD")
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
