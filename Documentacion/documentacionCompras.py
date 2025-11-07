"""
Servidor de Documentación - Sistema Distribuido de Compras/Ventas (Actualizado)
Autor: Molixx13
Fecha: 2025-11-06
Descripción:
---------------
Servidor HTTP que muestra la documentación del sistema de Compras/Ventas.
Versión actualizada para reflejar con precisión el flujo de artefacto_compras_ventas
contra Contabilidad, AtenciónProveedores, Tienda y Transportador.
Accesible desde cualquier navegador en la red local SIN autenticación (advertencia en doc).
"""

import http.server
import socketserver
import socket
import os
import base64

# =========================
# CONFIGURACIÓN
# =========================

PUERTO_DOCUMENTACION = 8093  # Puerto donde correrá el servidor de documentación

# =========================
# FUNCIONES
# =========================

def obtener_ip_local():
    """Obtiene la dirección IP local de esta máquina."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def cargar_imagen_equipo():
    """
    Intenta cargar la imagen del equipo y convertirla a base64.
    Busca: equipo.jpg, equipo.png, o equipo.jpeg
    Retorna:
    --------
    str : data URI de la imagen o string vacío si no existe
    """
    # Buscar en el directorio del script, en el directorio de trabajo actual y en 'docs/'
    extensiones = ['.jpg', '.jpeg', '.png', '.gif']
    script_dir = os.path.dirname(os.path.abspath(__file__))
    posibles_dirs = [script_dir, os.getcwd(), os.path.join(script_dir, 'docs')]

    for d in posibles_dirs:
        if not d or not os.path.isdir(d):
            continue
        try:
            for fname in os.listdir(d):
                name_low = fname.lower()
                base, ext = os.path.splitext(name_low)
                if not base.startswith('equipo'):
                    continue
                if ext not in extensiones:
                    continue

                path = os.path.join(d, fname)
                try:
                    with open(path, 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        mime_type = {
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.png': 'image/png',
                            '.gif': 'image/gif'
                        }.get(ext, 'image/jpeg')
                        print(f"✅ Imagen del equipo cargada: {path}")
                        return f"data:{mime_type};base64,{img_base64}"
                except Exception as e:
                    print(f"⚠️ Error cargando imagen '{path}': {e}")
        except Exception as e:
            # Si listar el directorio falla, seguir con el siguiente
            print(f"⚠️ No se pudo listar el directorio '{d}': {e}")

    # Si no se encuentra la imagen, retornar cadena vacía
    return ""


def crear_pagina_principal():
    """
    Crea la página HTML principal con documentación actualizada y precisa.
    """
    ip = obtener_ip_local()
    imagen_equipo = cargar_imagen_equipo()

    # Ajustable: opacidad del overlay oscuro que se aplica sobre la imagen de fondo
    # Si quieres la imagen más clara, reduce este valor (ej. 0.12). Para sin overlay, pon 0.
    overlay_opacity = 0.25

    fondo_body = (f"background-image: url('{imagen_equipo}'); background-size: cover; background-attachment: fixed; background-position: center;"
                  if imagen_equipo else "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);")

    # NOTA: se han actualizado los valores y descripciones para que coincidan
    # con el comportamiento real implementado en los módulos Python.

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación Sistema Distribuido - Compras/Ventas (Actualizado)</title>
    <style>/* Estilos condensados para legibilidad; se mantienen la mayor parte del diseño original */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; {fondo_body} min-height: 100vh; padding: 20px; position: relative; }}
    body::before {{ content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, {overlay_opacity if imagen_equipo else 0}); pointer-events: none; z-index: 0; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: rgba(255,255,255,0.98); border-radius: 20px; overflow: hidden; z-index: 1; padding-bottom: 40px; }}
        .header {{ background: linear-gradient(135deg,#667eea,#764ba2); color: white; padding: 30px 20px; text-align: center; }}
        .info-bar {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; padding:18px; background:#f8f9fa; border-bottom:3px solid #667eea; }}
        .info-item {{ padding:12px; background:white; border-radius:10px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.06); }}
        .value {{ font-weight:700; font-size:1.1em; color:#333; }}
        .content {{ padding:28px; }}
        .section {{ margin-bottom:30px; }}
        .module-card {{ background: linear-gradient(135deg,#667eea,#764ba2); color:white; padding:20px; border-radius:12px; box-shadow:0 8px 30px rgba(102,126,234,0.2); }}
        .code-block {{ background:#1e1e1e; color:#d4d4d4; padding:15px; border-radius:8px; font-family:monospace; overflow:auto; }}
        table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
        th,td {{ padding:12px; text-align:left; border-bottom:1px solid #e9ecef; }}
        th {{ background:#667eea; color:white; }}
        .flow-step {{ background:#fff; border-left:6px solid #667eea; padding:12px; margin:10px 0; border-radius:6px; }}
        .warning-box{{ background:#fff3cd; border-left:5px solid #ffc107; padding:12px; border-radius:6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Sistema Distribuido de Compras y Ventas</h1>
            <p>Documentación Técnica Actualizada — Flujo real de artefacto_compras_ventas y servicios relacionados</p>
            <p style="font-size:0.9em; margin-top:6px;">Autor: Molixx13 — Actualizado: 2025-11-06</p>
        </div>

        <div class="info-bar">
            <div class="info-item"><div class="label">📍 IP del Servidor</div><div class="value">{ip}</div></div>
            <div class="info-item"><div class="label">🔌 Puerto</div><div class="value">{PUERTO_DOCUMENTACION}</div></div>
            <div class="info-item"><div class="label">📚 Módulos</div><div class="value">5</div></div>
            <div class="info-item"><div class="label">🌐 Protocolo</div><div class="value">XML-RPC (payload JSON)</div></div>
        </div>

        <div class="content">
            <div class="section">
                <h2>📑 Índice Rápido</h2>
                <p>Comprende: artefacto_compras_ventas (middleware/orquestador), Contabilidad (asíncrono, autoridad de inventario), AtenciónProveedores (reabastecimiento), Tienda (cliente de ventas) y Transportador (servicio de logística).</p>
            </div>

            <div class="section" id="modulo1">
                <h2>🔹 Compras/Ventas — artefacto_compras_ventas.py</h2>

                <div class="module-card">
                    <h3>Descripción resumida</h3>
                    <p>Este módulo actúa como <strong>orquestador</strong> para ventas y el registro de compras. Es un servidor XML-RPC multihilo que expone APIs para: registrar ventas, registrar compras, consultar historial y proporcionar la IP local.</p>

                    <h4 style="margin-top:12px;">Configuración y parámetros importantes</h4>
                    <table>
                        <tr><th>Parámetro</th><th>Valor</th><th>Descripción</th></tr>
                        <tr><td>IP_CONTABILIDAD</td><td>http://25.21.199.213:10010</td><td>URL base del servicio de Contabilidad</td></tr>
                        <tr><td>PUERTO_COMPRAS_VENTAS</td><td>9000</td><td>Puerto donde escucha Compras/Ventas (ruta RPC: /rpc)</td></tr>
                        <tr><td>TIMEOUT GLOBAL</td><td>90s (socket.setdefaulttimeout)</td><td>Timeout por defecto para conexiones salientes RPC</td></tr>
                    </table>

                    <h4 style="margin-top:12px;">Funciones RPC expuestas</h4>
                    <ul>
                        <li><strong>registrar_venta(cliente, productos, total)</strong> — Normaliza entrada, crea id de venta, guarda en memoria y solicita factura a Contabilidad. Siempre registra la venta aun si Contabilidad no responde.</li>
                        <li><strong>registrar_compra(proveedor, productos, total, data)</strong> — Normaliza entrada, crea id de compra, guarda localmente y envía factura a Contabilidad (quien actualiza inventario).</li>
                        <li><strong>obtener_ip_local()</strong> — Retorna IP activa de la interfaz usada.</li>
                        <li><strong>consultar_ventas()/consultar_compras()/consultar_facturas()</strong> — Consultas para auditoría.</li>
                    </ul>
                </div>

                <h4 style="margin-top:14px;">Comportamiento detallado (¿cómo, cuándo y dónde?)</h4>
                <div class="flow-step">
                    <strong>Cómo</strong>: Cuando se llama <code>registrar_venta</code>, el módulo transforma la entrada (acepta str/JSON/dict), crea un ID de venta, almacena la venta en memoria (dict <code>ventas</code>) y luego intenta llamar a Contabilidad vía RPC (<code>generarFactura</code>) usando JSON como payload.
                </div>

                <div class="flow-step">
                    <strong>Cuándo</strong>: Se invoca inmediatamente desde el cliente (p. ej. <code>Tienda.py</code>) al confirmar una compra. La petición al servidor Compras/Ventas es síncrona desde el cliente, pero Compras/Ventas no espera indefinidamente: respeta timeouts de socket global (90s).
                </div>

                <div class="flow-step">
                    <strong>Dónde</strong>: El registro se guarda en memoria dentro del proceso de Compras/Ventas (estructura <code>ventas</code>). La generación de factura se solicita a Contabilidad (IP: 25.21.199.213:10010). Si Contabilidad responde, la factura se almacena en <code>facturas[id_venta]</code>.
                </div>

                <div class="warning-box" style="margin-top:10px;">
                    <strong>⚠️ Comportamiento contra fallos:</strong> Si Contabilidad no responde, la venta sigue registrada localmente y la función devuelve status="ok" pero con <code>factura</code> = <code>None</code>. Esto es por diseño para no interrumpir operaciones comerciales.
                </div>

                <h4 style="margin-top:12px;">Notas operativas y recomendaciones</h4>
                <ul>
                    <li>Usar un <strong>TimeoutTransport</strong> en clientes XML-RPC para evitar bloqueos largos al conectar con servicios externos.</li>
                    <li>Verificar que la ruta RPC sea <code>/rpc</code> (Contabilidad también acepta <code>/RPC2</code>), y que firewalls permitan los puertos listados.</li>
                    <li>Considerar persistencia periódica (dump a disco) para la estructura <code>ventas</code> si se requiere durabilidad entre reinicios.</li>
                </ul>
            </div>

            <div class="section" id="modulo2">
                <h2>🔹 Contabilidad — contabilidadRCP.py (Autoridad única de inventario)</h2>
                <div class="module-card">
                    <p>Contabilidad es la única responsable de generar facturas oficiales y actualizar inventario. Implementa procesamiento asíncrono: encola tareas para actualizar Inventario y responde INMEDIATAMENTE al llamador.</p>

                    <table>
                        <tr><th>Parámetro</th><th>Valor</th></tr>
                        <tr><td>IP</td><td>25.21.199.213</td></tr>
                        <tr><td>PUERTO</td><td>10010</td></tr>
                        <tr><td>Métodos</td><td><code>generarFactura(json_data)</code>, <code>recibirFactura(json_data)</code></td></tr>
                    </table>

                    <h4 style="margin-top:8px;">Comportamiento clave</h4>
                    <ul>
                        <li><strong>generarFactura:</strong> Recibe payload de venta, genera <code>factura_id</code> (FACT-YYYYMMDDHHMMSS), encola actualización de inventario y retorna la factura como JSON sin esperar que Inventario responda.</li>
                        <li><strong>recibirFactura:</strong> Recibe factura de compra, crea asiento, encola actualización de inventario (con cantidades/valores por defecto en la implementación actual) y retorna confirmación inmediata.</li>
                        <li>Worker daemon procesa la cola y llama a <code>Inventario.actualizarInventario()</code> en segundo plano.</li>
                    </ul>

                    <div class="warning-box" style="margin-top:10px;">
                        <strong>⚠️ Observación:</strong> Si la llamada RPC al servicio de Inventario falla, el worker registra el error y continúa procesando otras tareas. Es recomendable instrumentar reintentos y un dead-letter queue para casos de fallo prolongado.
                    </div>
                </div>
            </div>

            <div class="section" id="modulo3">
                <h2>🔹 Atención a Proveedores — atencion_provedores.py</h2>
                <div class="module-card">
                    <p>Recibe requerimientos de Inventario (cuando hay bajo stock), simula compra a proveedor, guarda historial en <code>compras_proveedores.json</code> y envía la orden a Compras/Ventas (<code>registrar_compra</code>).</p>

                    <p><strong>Puerto:</strong> 7005</p>
                    <p><strong>Comportamiento importante:</strong> <em>NO actualiza inventario</em>. Confía en que Contabilidad realizará la actualización.</p>
                </div>
            </div>

            <div class="section" id="modulo4">
                <h2>🔹 Tienda (cliente) y Transportador</h2>

                <div class="module-card">
                    <h3>Tienda.py</h3>
                    <p>Cliente interactivo que: lista productos desde Inventario, solicita compra a Compras/Ventas (<code>registrar_venta</code>) y, tras registrar la venta, invoca un servicio de transportador para coordinar el envío.</p>

                    <p><strong>Transportador:</strong> Servicio adicional (ejemplo: http://25.21.199.213:7000). Tienda invoca <code>ordenarTransporte(envio_data)</code> al transportador después de confirmar la venta.</p>

                    <div class="warning-box" style="margin-top:8px;">
                        <strong>⚠️ Nota técnica:</strong> En <code>Tienda.py</code> el valor de <code>TRANSPORTADOR_RPC_URL</code> no incluye <code>/rpc</code> en la constante; confirmar la ruta esperada por el servicio transportador (puede ser <code>/rpc</code> o raíz).</n                    </div>
                </div>
            </div>

            <div class="section" id="arquitectura">
                <h2>Arquitectura del Sistema (Resumen actualizado)</h2>
                <pre style="background:#1e1e1e;color:#4ec9b0;padding:12px;border-radius:8px;"> 
+-----------+        +-----------------------+        +-------------+      +------------+
|  Tienda   | -----> | Compras/Ventas (9000) | -----> | Contabilidad | ---> | Inventario |
| (cliente) |        | (orquestador)         |        | (10010)      |      | (8010/rpc) |
+-----------+        +-----------------------+        +-------------+      +------------+
       |                      |                            ^
       |                      |                            |
       |                      ----> AtenciónProveedores --->+
       |                             (7005)                (Contabilidad encola actualizaciones)
       |
       -----> Transportador (7000)  (servicio logístico llamado por Tienda)
                
Protocolos: XML-RPC sobre HTTP (payload JSON). Contabilidad procesa inventario en segundo plano para evitar bloqueos.
                </pre>

                <div class="warning-box">
                    <strong>⚠️ Seguridad y red:</strong> Este entorno NO implementa autenticación ni cifrado. Producción requiere TLS, autenticación mutua o VPN y control de acceso de red.
                </div>
            </div>

            <div class="section" id="instalacion">
                <h2>Instalación y Puesta en Marcha (orden recomendado)</h2>
                <ol>
                    <li><strong>Iniciar Contabilidad</strong> (puerto 10010) — autoridad de facturación e inventario.</li>
                    <li><strong>Iniciar Compras/Ventas</strong> (puerto 9000) — orquestador.</li>
                    <li><strong>Iniciar AtenciónProveedores</strong> (puerto 7005) — si aplica.</li>
                    <li><strong>Iniciar Transportador</strong> (puerto 7000) — servicio logístico.</li>
                    <li><strong>Iniciar clientes (Tienda, otras UIs)</strong>.</li>
                </ol>

                <div class="warning-box" style="margin-top:8px;">
                    <strong>⚠️ Firewall:</strong> Abra los puertos 10010, 9000, 7005 y 7000 según corresponda.
                </div>

                <h4 style="margin-top:12px;">Recomendaciones adicionales</h4>
                <ul>
                    <li>Usar <strong>timeout</strong> en conexiones RPC externas y configurar reintentos exponenciales en workers si la infraestructura lo requiere.</li>
                    <li>Agregar persistencia de ventas/compras/facturas en disco o base de datos si se necesita tolerancia a reinicios.</li>
                    <li>Instrumentar logging estructurado y métricas (latencia, tasa de facturas fallidas, tamaño de cola de Contabilidad).</li>
                </ul>
            </div>

            <div class="section">
                <h2>Ejemplo mínimo (cliente Python) — registrar_venta</h2>
                <div class="code-block">
# Cliente simple para registrar una venta
import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy('http://{ip}:9000/rpc', allow_none=True)
resp = server.registrar_venta('Ana', ['Silla Ergonómica x2'], 700000)
print(resp)
                </div>
            </div>

            <div class="section">
                <h2>Solución de Problemas (actualizada)</h2>
                <table>
                    <tr><th>Error</th><th>Causa</th><th>Solución</th></tr>
                    <tr><td>Contabilidad no responde</td><td>Servicio caído o red</td><td>Ver logs de Contabilidad; las ventas quedan registradas; revisar cola en Contabilidad.</td></tr>
                    <tr><td>Transportador devuelve error</td><td>URL/ruta incorrecta o servicio no expone /rpc</td><td>Confirmar TRANSPORTADOR_RPC_URL y método <code>ordenarTransporte</code>.</td></tr>
                    <tr><td>Timeout (90s)</td><td>Operación remota lenta</td><td>Revisar red; reducir timeout; agregar retries.</td></tr>
                    <tr><td>Permission denied (Address in use)</td><td>Puerto ocupado</td><td>Cerrar proceso previo o cambiar puerto.</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Glosario corto</h2>
                <table>
                    <tr><th>Término</th><th>Significado</th></tr>
                    <tr><td>Orquestador</td><td>Módulo que coordina acciones entre servicios (Compras/Ventas).</td></tr>
                    <tr><td>Autoridad de Inventario</td><td>Contabilidad — único módulo que actualiza stock en el sistema.</td></tr>
                    <tr><td>Worker</td><td>Hilo que procesa la cola asíncrona en Contabilidad.</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Advertencias finales</h2>
                <div class="warning-box">
                    • Este servidor de documentación NO implementa autenticación. No lo exponga a redes públicas.
                    <br>• Para entornos reales, implemente TLS, autenticación y control de acceso por IP/ACL.
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html


class SinAutenticacionHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handler HTTP que NO requiere autenticación.
    """
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = crear_pagina_principal()
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        ip_cliente = self.client_address[0]
        print(f"📡 Petición desde {ip_cliente}: {args[0]}")


def iniciar_servidor_documentacion():
    ip = obtener_ip_local()
    puerto = PUERTO_DOCUMENTACION

    print("\n" + "="*70)
    print("📚 SERVIDOR DE DOCUMENTACIÓN (ACTUALIZADO) INICIADO")
    print("="*70)
    print(f"📍 IP de este servidor:  {ip}")
    print(f"🔌 Puerto:               {puerto}")
    print(f"🌐 URL de acceso:        http://{ip}:{puerto}")
    print("="*70)

    imagen = cargar_imagen_equipo()
    if imagen:
        print("\n✨ ¡Imagen personalizada detectada y cargada!")
    else:
        print("\n💡 Usando fondo por defecto (degradado)")

    print("\n⏳ Servidor corriendo. Presiona Ctrl+C para detener.\n")

    with socketserver.TCPServer(("0.0.0.0", puerto), SinAutenticacionHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Servidor detenido por el usuario")
            print("👋 ¡Hasta pronto!\n")


# =========================
# EJECUCIÓN PRINCIPAL
# =========================

if __name__ == "__main__":
    try:
        iniciar_servidor_documentacion()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}\n")
