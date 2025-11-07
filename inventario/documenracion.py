#!/usr/bin/env python3
# documentacion_inventario_dual.py
# Servidor de documentación (oscuro) para Inventario dual (persistente + unificado)
# Autor: Generado por asistente para Molixx13
# Puerto: 8085

import http.server
import socketserver
import socket
import json
import os
from string import Template
import html
from urllib.parse import urlparse, unquote

PORT = 8091
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ruta presumida del inventario (ajusta si tu estructura difiere)
INVENTARIO_JSON = os.path.join(BASE_DIR, "inventario", "inventario_data.json")


def obtener_ip_local() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def cargar_inventario_preview(max_items: int = 10):
    """
    Intenta leer INVENTARIO_JSON y devuelve:
      - tabla_html (str) con filas (hasta max_items)
      - raw_json_escaped (str) con JSON escapado para mostrar en el HTML (no para parsing)
    Si no existe o falla, devuelve mensajes informativos.
    """
    if not os.path.exists(INVENTARIO_JSON):
        notice = "<tr><td colspan='5'>No se encontró inventario_data.json en la ruta esperada.</td></tr>"
        return notice, html.escape("{}")
    try:
        with open(INVENTARIO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        notice = f"<tr><td colspan='5'>Error leyendo JSON: {html.escape(str(e))}</td></tr>"
        return notice, html.escape("{}")
    # data puede ser dict con "productos" o dict de productos por id
    productos_list = []
    # try common shapes
    if isinstance(data, dict) and "productos" in data:
        productos_list = data.get("productos") or []
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        productos_list = data["data"]
    else:
        # If stored as dict keyed by id
        try:
            # filter values that look like producto dicts
            productos_list = [v for v in data.get("productos", {}).values()] if isinstance(data, dict) else []
            if not productos_list:
                # try all dict values
                productos_list = [v for v in data.values() if isinstance(v, dict) and "nombre" in v]
        except Exception:
            productos_list = []

    # fallback: if still empty, try treat top-level as products mapping
    if not productos_list and isinstance(data, dict):
        productos_list = []
        for k, v in data.items():
            if isinstance(v, dict) and "nombre" in v:
                productos_list.append(v)

    # build table rows
    rows = []
    for p in productos_list[:max_items]:
        pid = html.escape(str(p.get("id", "")))
        nombre = html.escape(str(p.get("nombre", p.get("nombre", "Sin nombre"))))
        stock = html.escape(str(p.get("stock", p.get("cantidad", ""))))
        precio = html.escape(str(p.get("precio", p.get("precio_unit", ""))))
        stock_min = html.escape(str(p.get("stock_minimo", p.get("stock_min", ""))))
        rows.append(f"<tr><td>{pid}</td><td>{nombre}</td><td style='text-align:right'>{stock}</td>"
                    f"<td style='text-align:right'>{precio}</td><td style='text-align:right'>{stock_min}</td></tr>")

    if not rows:
        rows = ["<tr><td colspan='5'>No se encontraron productos interpretables en inventario_data.json</td></tr>"]

    table_html = "\n".join(rows)
    raw_json_escaped = html.escape(json.dumps(data, indent=2, ensure_ascii=False))
    return table_html, raw_json_escaped


# Simple ASCII / SVG diagram minimal
SVG_DIAGRAMA = """
<svg width="560" height="140" viewBox="0 0 560 140" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <style>
    .box{fill:#0f1724;stroke:#1f2937;stroke-width:1;rx:8;ry:8}
    .text{fill:#cbd5e1;font-family:Segoe UI,Arial,Helvetica,sans-serif;font-size:12px}
    .arrow{stroke:#60a5fa;stroke-width:2;fill:none;marker-end:url(#arrowhead)}
  </style>
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#60a5fa"/>
    </marker>
  </defs>
  <rect class="box" x="10" y="20" width="140" height="40" />
  <text class="text" x="20" y="45">Tienda (cliente)</text>

  <rect class="box" x="200" y="10" width="170" height="60" />
  <text class="text" x="215" y="35">Compras/Ventas (Orquestador)</text>

  <rect class="box" x="410" y="10" width="140" height="60" />
  <text class="text" x="420" y="35">Contabilidad</text>

  <path class="arrow" d="M150,40 L200,40" />
  <path class="arrow" d="M370,40 L410,40" />

  <rect class="box" x="200" y="85" width="140" height="40" />
  <text class="text" x="215" y="110">Inventario RPC</text>

  <path class="arrow" d="M270,70 L270,85" />
</svg>
"""

# HTML template using string.Template (dollar placeholders)
HTML_TEMPLATE = Template("""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Documentación - Inventario Dual (Persistente + Unificado)</title>
<style>
  :root { --bg:#0d1117; --panel:#0b1220; --muted:#9aa4b2; --accent:#60a5fa; --card:#0f1724; --mono: "Fira Code", "Courier New", monospace; }
  body { margin:0; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; background:var(--bg); color:#cbd5e1; }
  header { padding:18px 28px; background:linear-gradient(90deg, rgba(2,6,23,0.9), rgba(7,10,24,0.95)); border-bottom:1px solid #0b1220; }
  h1 { margin:0; font-size:20px; color:#e6eef8; }
  .meta { color:var(--muted); font-size:13px; margin-top:6px; }
  main { max-width:1100px; margin:20px auto; padding:18px; }
  .card { background:var(--card); border-radius:10px; padding:16px; box-shadow: 0 8px 30px rgba(2,6,23,0.6); margin-bottom:18px; border:1px solid #121827; }
  .grid { display:grid; grid-template-columns: 1fr 360px; gap:18px; align-items:start; }
  pre.code { background:#07080a; padding:12px; border-radius:8px; color:#9ae6ff; overflow:auto; font-family:var(--mono); font-size:13px; }
  table { width:100%; border-collapse:collapse; margin-top:8px; font-size:13px; color:#d1d5db; }
  th, td { padding:10px; text-align:left; border-bottom:1px solid #0b1220; }
  th { background: linear-gradient(90deg,#071028,#0b1220); color:#cfe8ff; font-weight:600; }
  .muted { color:var(--muted); font-size:13px; }
  .pill { display:inline-block; padding:6px 10px; background:#071224; border-radius:999px; color:#9fd3ff; border:1px solid #0b1f35; font-size:12px; }
  .section-title { font-size:16px; color:#e6eef8; margin-bottom:8px; }
  details { background:linear-gradient(90deg,#071224,#071225); padding:10px; border-radius:8px; border:1px solid #0b1220; }
  summary { cursor:pointer; outline:none; font-weight:600; color:#cfe8ff; }
  .diagram { background:linear-gradient(90deg,#071224,#061022); padding:10px; border-radius:8px; text-align:center; }
  a.link { color:var(--accent); text-decoration:none; }
  footer { max-width:1100px; margin:12px auto 40px; color:var(--muted); font-size:13px; text-align:center; }
</style>
</head>
<body>
<header>
  <h1>Inventario Dual — Documentación Técnica</h1>
  <div class="meta">Servicio RPC persistente + servidor RPC unificado — Autor: Molixx13 — Actualizado: 2025-11-06</div>
</header>

<main>
  <div class="card">
    <div class="section-title">Resumen ejecutivo (parte de la documentación dinámica)</div>
    <div class="muted">Se muestra un preview del archivo de persistencia y un endpoint /data para descargar el JSON completo.</div>
    <div style="margin-top:12px;">
      <span class="pill">Puerto RPC: 8010</span>
      <span class="pill" style="margin-left:8px">Docs dinámicas: Sí</span>
      <span class="pill" style="margin-left:8px">Tema: Oscuro</span>
    </div>
  </div>

  <div class="grid">
    <div>
      <div class="card">
        <div class="section-title">Inventario (persistente) — Descripción detallada</div>
        <p class="muted">Servicio XML-RPC que guarda su estado en <code>inventario_data.json</code>. Opera con estructuras: productos (id, nombre, descripcion, categoria, precio, stock, stock_minimo) y requerimientos.</p>

        <details open>
          <summary>Contrato RPC — Métodos expuestos</summary>
          <div style="margin-top:8px;">
            <ul>
              <li><code>cargarProductos(nombre, descripcion, categoria, precio, stock, stock_minimo=5)</code> → agrega producto y persiste</li>
              <li><code>actualizarInventario(producto_id / data)</code> → actualiza stock/precio; maneja operaciones tipo <code>VENTA</code> y <code>COMPRA</code></li>
              <li><code>listarProductos()</code>, <code>obtenerProducto(id)</code>, <code>listarRequerimientos()</code>, <code>estadisticasInventario()</code>, <code>healthCheck()</code></li>
            </ul>
          </div>
        </details>

        <details>
          <summary>Flujos y comportamiento (muy detallado)</summary>
          <div style="margin-top:8px;">
            <ol>
              <li><strong>Venta:</strong> recibe payload tipo <code>VENTA</code> con lista de productos. Decrementa stock, persiste y si stock ≤ stock_minimo encola requerimiento.</li>
              <li><strong>Compra:</strong> recibe payload tipo <code>COMPRA</code> desde Contabilidad/Compras. Incrementa stock y actualiza precio si <code>precio_unit</code> &gt; 0.</li>
              <li><strong>Requerimiento automático:</strong> cuando algún producto alcanza bajo stock, se construye JSON y se llama a AtenciónProveedores (ruta definida en constante).</li>
              <li><strong>Persistencia:</strong> cada cambio llama a <code>guardar_datos()</code> que vuelca el estado en disco (ruta absoluta).</li>
            </ol>
          </div>
        </details>

        <details>
          <summary>Errores comunes y soluciones</summary>
          <div style="margin-top:8px;">
            <ul>
              <li><strong>Producto no encontrado:</strong> la función imprime advertencia y continúa; revisar nombres/normalización (se compara lower()).</li>
              <li><strong>Formato JSON inválido:</strong> las funciones intentan parsear strings JSON; enviar siempre JSON string o dict según contratos.</li>
              <li><strong>Conectividad a AtenciónProveedores:</strong> usa transporte custom para forzar <code>/rpc</code> (evita 404 por /RPC2).</li>
            </ul>
          </div>
        </details>

        <div style="margin-top:12px;">
          <div class="section-title">Preview del inventario (hasta 10 entradas)</div>
          <table>
            <thead><tr><th>ID</th><th>Nombre</th><th style="text-align:right">Stock</th><th style="text-align:right">Precio</th><th style="text-align:right">Stock mínimo</th></tr></thead>
            <tbody>
            $productos_table
            </tbody>
          </table>
          <div style="margin-top:10px;" class="muted">Si deseas descargar el JSON completo, visita <a class="link" href="/data">/data</a>.</div>
        </div>

      </div>

      <div class="card">
        <div class="section-title">Servidor RPC Unificado — Detalles operativos</div>
        <p class="muted">El servidor unificado expone los mismos métodos del servicio persistente y además registra funciones de introspección. Soporta multithreading (ThreadingMixIn + SimpleXMLRPCServer).</p>

        <details>
          <summary>Inicio y parada segura</summary>
          <div style="margin-top:8px;">
            <pre class="code">
# Ejecutar:
python inventario_server.py

# Parada (Ctrl+C):
El servidor captura KeyboardInterrupt, llama a guardar_datos() y cierra el server.
            </pre>
          </div>
        </details>
      </div>

    </div>

    <aside>
      <div class="card diagram">
        <div class="section-title">Diagrama simplificado</div>
        $svg_diagram
      </div>

      <div class="card">
        <div class="section-title">JSON (raw preview)</div>
        <pre class="code" style="max-height:300px; overflow:auto;">$raw_json</pre>
      </div>

      <div class="card">
        <div class="section-title">Quick Links</div>
        <ul>
          <li><a class="link" href="/data">Descargar inventario_data.json</a></li>
          <li><a class="link" href="http://$host:$port/rpc">Prueba endpoint RPC (no browser)</a></li>
        </ul>
      </div>
    </aside>
  </div>

  <div class="card">
    <div class="section-title">Detalles técnicos y recomendaciones (extenso)</div>
    <div class="muted">
      - Validar tipos (int/float) antes de persistir. <br/>
      - Usar transporte con timeout en clientes XML-RPC (ver ejemplo en docs de Compras/Ventas). <br/>
      - Instrumentar métricas y DLQ para requerimientos fallidos. <br/>
      - No exponer en redes públicas sin TLS + autenticación.
    </div>
  </div>

</main>

<footer>
  Servidor documentación — Inventario Dual • IP $host • puerto $port — Tema: Oscuro
</footer>
</body>
</html>
""")

class DocHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        host = obtener_ip_local()
        if path in ("/", "/index.html"):
            table_html, raw_json = cargar_inventario_preview()
            # Substitute placeholders
            html_out = HTML_TEMPLATE.substitute(
                productos_table=table_html,
                raw_json=raw_json,
                svg_diagram=SVG_DIAGRAMA,
                host=host,
                port=str(PORT)
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'unsafe-inline' 'self'")
            self.end_headers()
            self.wfile.write(html_out.encode("utf-8"))
            return

        if path == "/data":
            # serve raw JSON (no html escaping) for download/inspection
            if os.path.exists(INVENTARIO_JSON):
                try:
                    with open(INVENTARIO_JSON, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Disposition", "attachment; filename=\"inventario_data.json\"")
                    self.end_headers()
                    self.wfile.write(data)
                except Exception as e:
                    self.send_error(500, "Error leyendo archivo: " + str(e))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"{}")
            return

        # fallback to default handler (serve files if any)
        return super().do_GET()

def run_server():
    host_ip = obtener_ip_local()
    print("\n" + "="*70)
    print("📚 SERVIDOR DE DOCUMENTACIÓN - INVENTARIOS (DUAL)")
    print("="*70)
    print(f"📍 IP: {host_ip}")
    print(f"🔌 Puerto: {PORT}")
    print(f"🌐 URL: http://{host_ip}:{PORT}/")
    print("="*70 + "\n")
    with socketserver.TCPServer(("0.0.0.0", PORT), DocHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por usuario")
        finally:
            httpd.server_close()

if __name__ == "__main__":
    run_server()
