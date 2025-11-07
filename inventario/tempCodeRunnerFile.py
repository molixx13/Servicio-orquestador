"""
Servidor de Documentación para Módulos de Inventario (Dual)
Autor: Molixx13
Fecha: 2025-11-06
Descripción:
-------------
Servidor HTTP que entrega una documentación técnica extensa y profesional
para los dos artefactos de inventario del proyecto:
 - inventario_service.py (clase InventarioService: lógica y persistencia)
 - inventario_server.py  (servidor RPC unificado + doc web estática)

El servidor corre en el puerto 8082 y expone una única página HTML en /
con contenido detallado, diagramas SVG inline, ejemplos de payload,
secuencias y recomendaciones operativas.

Ejecución:
    python documentacion_inventarios.py
Abrir en navegador:
    http://<IP_LOCAL>:8082/

Nota: la página está diseñada con fondo claro y cajas para evitar que
el texto se mezcle con cualquier fondo de pantalla del host.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import json
from textwrap import dedent

PORT = 8082


def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def crear_html_documentacion(ip, port):
    """
    Construye el HTML de documentación. Usamos marcadores %%IP%% y %%PORT%%
    para insertar la IP/PUERTO sin tener que usar formateo que choque con
    llaves JSON en el contenido.
    """

    # SVG diagrama (simple) -- dos inventarios y sus relaciones
    svg_diagrama = dedent(r'''
    <svg width="900" height="220" viewBox="0 0 900 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de Inventarios">
      <style>
        .box { fill:#ffffff; stroke:#2b6cb0; stroke-width:2px; rx:8; }
        .title { font: 14px sans-serif; fill:#1a202c; font-weight:700 }
        .text { font: 12px sans-serif; fill:#2d3748 }
        .arrow { stroke:#2b6cb0; stroke-width:2; marker-end:url(#arrowhead);} 
      </style>
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#2b6cb0" />
        </marker>
      </defs>

      <!-- Inventario persistente (InventarioService) -->
      <rect class="box" x="20" y="20" width="260" height="120"/>
      <text class="title" x="40" y="45">InventarioService (persistente)</text>
      <text class="text" x="40" y="70">- Archivo: inventario_data.json</text>
      <text class="text" x="40" y="90">- API: listarProductos, actualizarInventario, cargarProductos</text>
      <text class="text" x="40" y="110">- Lógica local: bajo stock → generar requerimiento</text>

      <!-- Inventario RPC unificado (Servidor) -->
      <rect class="box" x="620" y="20" width="260" height="120"/>
      <text class="title" x="640" y="45">Servidor Inventario (RPC)</text>
      <text class="text" x="640" y="70">- Archivo: inventario_server.py</text>
      <text class="text" x="640" y="90">- Expone /rpc, ruta: http://%%IP%%:8010/rpc</text>
      <text class="text" x="640" y="110">- Web docs: http://%%IP%%:8080/</text>

      <!-- Contabilidad (ejemplo) -->
      <rect class="box" x="320" y="20" width="220" height="120"/>
      <text class="title" x="340" y="45">Contabilidad (autoridad)</text>
      <text class="text" x="340" y="70">- Genera facturas</text>
      <text class="text" x="340" y="90">- Encola actualizaciones de inventario</text>

      <!-- Flechas -->
      <line class="arrow" x1="290" y1="70" x2="320" y2="70" />
      <line class="arrow" x1="540" y1="70" x2="620" y2="70" />

      <!-- Leyenda -->
      <text class="text" x="20" y="160">Diagrama: flujo simplificado (Compras/Ventas → Contabilidad → Inventario)</text>
    </svg>
    ''')

    # HTML principal -- extensamente detallado
    html = """
    <!doctype html>
    <html lang="es">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Documentación Técnica — Inventarios (Dual)</title>
      <style>
        :root{--accent:#2b6cb0;--muted:#6b7280;--bg:#ffffff}
        html,body{height:100%;margin:0;background:var(--bg);font-family:Inter,Segoe UI,Arial,Helvetica,sans-serif;color:#111827}
        .wrap{max-width:1200px;margin:28px auto;padding:26px;background:#f8fafc;border-radius:12px;box-shadow:0 8px 30px rgba(2,6,23,0.06)}
        header{display:flex;gap:20px;align-items:center}
        header h1{margin:0;font-size:22px;color:var(--accent)}
        .meta{color:var(--muted);font-size:13px}
        .grid{display:grid;grid-template-columns:1fr 360px;gap:20px;margin-top:18px}
        .card{background:white;padding:18px;border-radius:10px;box-shadow:0 4px 16px rgba(15,23,42,0.04)}
        h2{color:#0f172a;margin-top:0}
        pre.code{background:#0f172a;color:#e6eef8;padding:12px;border-radius:8px;overflow:auto;font-family:Menlo,monospace;font-size:13px}
        table{width:100%;border-collapse:collapse}
        th,td{padding:8px;border-bottom:1px solid #eef2f7;text-align:left}
        th{background:var(--accent);color:white}
        .section{margin-bottom:18px}
        .small{font-size:13px;color:var(--muted)}
        .note{background:#fffbea;border-left:4px solid #f59e0b;padding:10px;border-radius:6px}
        .success{background:#ecfdf5;border-left:4px solid #10b981;padding:10px;border-radius:6px}
      </style>
    </head>
    <body>
      <div class="wrap">
        <header>
          <div>
            <h1>Servicio de Inventario — Documentación Técnica (Dual)</h1>
            <div class="meta">Autor: Molixx13 • Actualizado: 2025-11-06</div>
          </div>
          <div style="margin-left:auto;text-align:right" class="small">
            Endpoint RPC (unificado): <strong>http://%%IP%%:8010/rpc</strong><br>
            Docs web (local): <strong>http://%%IP%%:8080/</strong><br>
            Página de documentación actual: <strong>http://%%IP%%:%%PORT%%/</strong>
          </div>
        </header>

        <div class="grid">
          <div>

            <section class="card section">
              <h2>Resumen ejecutivo</h2>
              <p>Este repositorio contiene dos artefactos de inventario que conviven y colaboran en
              el sistema distribuido:</p>
              <ol>
                <li><strong>InventarioService (inventario_service.py)</strong>: la clase que implementa la
                lógica de negocio, persistencia en <code>inventario_data.json</code> y el comportamiento
                de detección de bajo stock (genera requerimientos a AtenciónProveedores).</li>
                <li><strong>Servidor Inventario (inventario_server.py)</strong>: la envoltura RPC/multihilo que
                registra los métodos y expone la API /rpc; además arranca un servidor web estático para
                la documentación (puerto 8080).</li>
              </ol>
              <p class="small">Objetivo: ofrecer una especificación técnica completa, ejemplos de payload,
              secuencias, y guías operativas para desarrolladores y operadores.</p>
            </section>

            <section class="card section">
              <h2>Inventario: responsabilidades y alcance</h2>
              <ul>
                <li>Almacenar catálogo de productos con: id, nombre, descripción, categoría, precio, stock y stock_minimo.</li>
                <li>Actualizar stock por VENTA/COMPRA o por actualización directa.</li>
                <li>Generar requerimientos automáticos cuando el stock cae por debajo del umbral.</li>
                <li>Persistir el estado en disco para tolerancia a reinicios.</li>
                <li>Exponer APIs consultivas para listar y obtener productos, estadísticas y health check.</li>
              </ul>
            </section>

            <section class="card section">
              <h2>API RPC (detallada)</h2>
              <table>
                <tr><th>Método</th><th>Descripción</th><th>Entrada / Salida</th></tr>
                <tr><td>cargarProductos</td><td>Añade un producto nuevo</td><td><pre class="code">(nombre, descripcion, categoria, precio, stock, stock_minimo=5)
Retorna: {"success": True, "producto_id": <int>, "data": {...}}</pre></td></tr>
                <tr><td>actualizarInventario</td><td>Actualiza stock/precio; procesa VENTA/COMPRA</td><td><pre class="code">Entrada: dict o JSON string
-- Campos relevantes:
  tipo_operacion: 'VENTA' | 'COMPRA' | 'ACTUALIZACION'
  productos: [{"nombre":"Silla","cantidad":1,"precio_unit":100000}]
Retorna: {'status':'ok', 'message':...} o {'status':'error', 'detalle':...}
</pre></td></tr>
                <tr><td>listarProductos</td><td>Devuelve catálogo</td><td><pre class="code">{'success':True,'total_productos':N,'data':[...product objects...]}</pre></td></tr>
                <tr><td>obtenerProducto</td><td>Devuelve un producto por ID</td><td><pre class="code">(producto_id) -> {'success':True,'data':{...}}</pre></td></tr>
                <tr><td>listarRequerimientos</td><td>Requerimientos generados por bajo stock</td><td><pre class="code">{'success':True,'total_requerimientos':M,'data':[...]} </pre></td></tr>
                <tr><td>estadisticasInventario</td><td>Estadísticas agregadas</td><td><pre class="code">{'success':True,'estadisticas':{...}}</pre></td></tr>
              </table>
            </section>

            <section class="card section">
              <h2>Formato esperado de payloads (ejemplos)</h2>

              <h4>Venta (para actualizarInventario)</h4>
              <pre class="code">{
  "tipo_operacion": "VENTA",
  "nombre_cliente": "Ana",
  "productos": [
    {"nombre": "Silla Ergonómica", "cantidad": 2, "precio_unit": 350000}
  ],
  "total": 700000
}
              </pre>

              <h4>Compra (para actualizarInventario)</h4>
              <pre class="code">{
  "tipo_operacion": "COMPRA",
  "nombre_proveedor": "ProveedorXYZ",
  "productos": [
    {"nombre": "Mesa", "cantidad": 10, "precio_unit": 100000}
  ],
  "total": 1000000
}
              </pre>

              <div class="note">
                <strong>Nota:</strong> El servicio acepta dicts directos o JSON strings. Si envías cadenas
                JSON, asegúrate de serializarlas con <code>json.dumps()</code> antes de pasarlas por RPC.
              </div>
            </section>

            <section class="card section">
              <h2>Comportamiento en caso de bajo stock</h2>
              <p>Cuando una <strong>VENTA</strong> reduce el stock y el nuevo stock es &lt;= stock_minimo,
              se ejecuta <code>cargarRequerimientosProductos()</code> que:</p>
              <ol>
                <li>Busca productos con stock <= stock_minimo</li>
                <li>Genera un objeto <code>requerimiento</code> con lista de productos y cantidades (default: stock_minimo*2)</li>
                <li>Envía el requerimiento al servicio AtenciónProveedores vía XML-RPC (ruta configurada en ATENCION_PROVEEDORES_RPC_URL)</li>
                <li>Registra la respuesta y devuelve un estado</li>
              </ol>
              <div class="note">
                <strong>Transport edge-case:</strong> el módulo usa un <code>CustomTransport</code> que fuerza la ruta <code>/rpc</code>
                para evitar inconsistencias entre /RPC2 y /rpc en otros servicios.
              </div>
            </section>

            <section class="card section">
              <h2>Persistencia y estructura del archivo</h2>
              <p>El archivo <code>inventario_data.json</code> contiene un objeto con claves:</p>
              <pre class="code">{
  "productos": {"1": {"id":1,"nombre":"Silla",...}, "2": {...}},
  "requerimientos": {...},
  "next_product_id": 42,
  "next_requerimiento_id": 3
}
              </pre>

              <p class="small">El servicio convierte claves de producto a enteros al cargar para evitar inconsistencias.</p>
            </section>

            <section class="card section">
              <h2>Secuencia (ejemplo completo)</h2>
              <pre class="code">1) Tienda -> compras_rpc.registrar_venta(...)
2) Compras/Ventas -> contabilidad.generarFactura(json.dumps(payload_venta))
3) Contabilidad -> encola actualización (worker)
4) Worker -> inventario.actualizarInventario(json.dumps(envio_data))
5) Inventario -> actualiza stock, detecta bajo stock -> carga requerimiento
6) Inventario -> atencion_proveedores.procesarRequerimiento(json.dumps(req))
7) AtenciónProveedores -> registra compra y notifica Compras/Ventas
8) Compras/Ventas -> llama a contabilidad.recibirFactura(...) y contabilidad encola compra
</pre>
            </section>

            <section class="card section">
              <h2>Buenas prácticas y recomendaciones operativas</h2>
              <ul>
                <li>Siempre serializar JSON para RPC: <code>json.dumps(obj)</code> cuando el receptor espera string.</li>
                <li>Usar transports con timeout para ServerProxy (evitar bloqueos largos).</li>
                <li>Monitorizar el tamaño de inventario_data.json y considerar migrar a DB si crece mucho.</li>
                <li>Agregar pruebas que simulen Inventario caído para validar DLQ/eras en Contabilidad.</li>
                <li>Validar y normalizar cadenas entrantes (trim, case-insensitive matching para nombres de producto).
                </li>
              </ul>
            </section>

          </div>

          <aside>
            <div class="card section">
              <h3>Diagrama</h3>
              <div style="background:white;padding:8px;border-radius:6px">%s</div>
            </div>

            <div class="card section">
              <h3>Health & operaciones</h3>
              <p class="small">Puntos de verificación:</p>
              <ul>
                <li><code>GET /rpc</code> (introspección habilitada) — comprobar métodos.</li>
                <li>Archivo: <code>%s</code></li>
                <li>Comando: arrancar el servidor con <code>python inventario_server.py</code></li>
              </ul>
            </div>

            <div class="card section">
              <h3>Solución de Problemas — Errores comunes</h3>
              <table>
                <tr><th>Error</th><th>Causa probable</th></tr>
                <tr><td>Producto no encontrado</td><td>Nombre enviado no coincide (case/trim) o no existe en catálogo</td></tr>
                <tr><td>Timeout RPC</td><td>Servicio remoto caído o firewall</td></tr>
                <tr><td>Archivo JSON corrupto</td><td>Formato inválido; restaurar desde backup</td></tr>
                <tr><td>404 /RPC2 vs /rpc</td><td>Rutas diferentes entre servicios — usar CustomTransport o alinear rutas</td></tr>
              </table>
            </div>

            <div class="card section">
              <h3>Contactos</h3>
              <p class="small">Equipo: Equipo de Integración • Slack: #sistemas • Ops: ops@example.local</p>
            </div>

          </aside>
        </div>

        <footer style="margin-top:18px;text-align:center;color:var(--muted);font-size:13px">
          Documentación generada dinámicamente. No exponer en redes públicas sin autenticación.
        </footer>

      </div>
    </body>
    </html>
    """ % (svg_diagrama, os.path.join('..','inventario','inventario_data.json'))

    # Reemplazar marcadores
    html = html.replace('%%IP%%', ip).replace('%%PORT%%', str(port))
    return html


class DocHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            ip = obtener_ip_local()
            html = crear_html_documentacion(ip, PORT)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def log_message(self, format, *args):
        # Mensaje de log corto
        print("[DOC] %s - %s" % (self.client_address[0], format%args))


def run_server():
    ip = obtener_ip_local()
    httpd = HTTPServer(('0.0.0.0', PORT), DocHandler)
    print('\n' + '='*70)
    print('📚 SERVIDOR DE DOCUMENTACIÓN - INVENTARIOS (DUAL)')
    print('='*70)
    print(f'📍 IP: {ip}')
    print(f'🔌 Puerto: {PORT}')
    print(f'🌐 URL: http://{ip}:{PORT}/')
    print('='*70 + '\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Servidor detenido por el usuario')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run_server()
