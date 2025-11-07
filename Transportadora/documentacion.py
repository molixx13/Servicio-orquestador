"""
Servidor de Documentación - Transportador (Sistema Orquestado de Tienda de Muebles)
Autor: Molixx13
Fecha: 2025-11-07
Descripción:
---------------
Servidor HTTP que muestra la documentación técnica detallada del módulo Transportador.
Basado en el servidor de documentación para Compras/Ventas y AtenciónProveedores, adaptado para reflejar con precisión
el flujo y comportamiento de transportador.py. Incluye descripciones de métodos RPC,
flujos de operación, integración con otros módulos y recomendaciones.
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

PUERTO_DOCUMENTACION = 8095  # Puerto diferente para evitar conflictos con otros servidores de doc

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
    script_dir = os.path.dirname(os.path.abspath(__file__ if '__file__' in globals() else ''))
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
            print(f"⚠️ No se pudo listar el directorio '{d}': {e}")

    return ""


def crear_pagina_principal():
    """
    Crea la página HTML principal con documentación técnica detallada para Transportador.
    """
    ip = obtener_ip_local()
    imagen_equipo = cargar_imagen_equipo()

    # Ajustable: opacidad del overlay oscuro que se aplica sobre la imagen de fondo
    # Si quieres la imagen más clara, reduce este valor (ej. 0.12). Para sin overlay, pon 0.
    overlay_opacity = 0.25

    fondo_body = (f"background-image: url('{imagen_equipo}'); background-size: cover; background-attachment: fixed; background-position: center;"
                  if imagen_equipo else "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación Técnica - Transportador (Sistema Orquestado)</title>
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
            <h1>🚚 Módulo de Transportador</h1>
            <p>Documentación Técnica Detallada — Sistema Orquestado de Tienda de Muebles</p>
            <p style="font-size:0.9em; margin-top:6px;">Autor: Molixx13 — Fecha: 2025-11-07</p>
        </div>
        <div class="info-bar">
            <div class="info-item"><div class="label">📍 IP del Servidor</div><div class="value">{ip}</div></div>
            <div class="info-item"><div class="label">🔌 Puerto Doc</div><div class="value">{PUERTO_DOCUMENTACION}</div></div>
            <div class="info-item"><div class="label">🔌 Puerto RPC</div><div class="value">7000</div></div>
            <div class="info-item"><div class="label">🌐 Protocolo</div><div class="value">XML-RPC (ruta: /rpc)</div></div>
        </div>
        <div class="content">
            <div class="section">
                <h2>📑 Índice Rápido</h2>
                <p>Este módulo gestiona el transporte y entrega de productos vendidos. Recibe órdenes de envío desde Tienda o Compras/Ventas, almacena en JSON local y confirma el despacho.</p>
            </div>
            <div class="section" id="descripcion">
                <h2>🔹 Descripción General</h2>
                <div class="module-card">
                    <h3>Responsabilidades Principales</h3>
                    <ul>
                        <li>Recibir órdenes de envío de productos vendidos.</li>
                        <li>Registrar envíos en archivo JSON local (envios_data.json).</li>
                        <li>Confirmar el despacho con estado "Despachado".</li>
                        <li>Proporcionar lista de envíos registrados.</li>
                        <li><strong>Importante:</strong> Simula el transporte; no integra con servicios externos reales.</li>
                    </ul>
                    <h4 style="margin-top:12px;">Arquitectura y Flujo Típico</h4>
                    <p>Servidor XML-RPC simple escuchando en puerto 7000 (ruta sugerida /rpc). Comunicación unidireccional: Tienda/Compras → Transportador.</p>
                    <ol>
                        <li>Tienda o Compras llama a ordenarTransporte() con datos del pedido.</li>
                        <li>Parsea datos, logs en consola.</li>
                        <li>Registra envío en JSON con estado "Despachado".</li>
                        <li>Retorna confirmación.</li>
                    </ol>
                    <h4 style="margin-top:12px;">Dependencias</h4>
                    <table>
                        <tr><th>Módulo</th><th>URL</th><th>Propósito</th></tr>
                        <tr><td>Tienda / Compras/Ventas</td><td>Indirecto (llamadores)</td><td>Origen de órdenes de envío</td></tr>
                    </table>
                </div>
            </div>
            <div class="section" id="metodos">
                <h2>🔹 Métodos RPC Expuestos</h2>
                <div class="module-card">
                    <h3>ordenarTransporte(json_data: str or dict) → Dict[str, Any]</h3>
                    <p>Registra un nuevo envío basado en los datos del pedido.</p>
                    <h4>Argumentos</h4>
                    <ul>
                        <li><strong>json_data</strong>: JSON string o dict con {{'cliente': str, 'producto': str, 'cantidad': int, 'total': int}}.</li>
                    </ul>
                    <h4>Retorno</h4>
                    <ul>
                        <li>Dict con {{'status': 'ok/error', 'mensaje' or 'detalle': str}}.</li>
                    </ul>
                    <h3>listarEnvios() → Dict[str, Any]</h3>
                    <p>Retorna todos los envíos registrados.</p>
                    <h4>Retorno</h4>
                    <ul>
                        <li>Dict con {{'total': int, 'data': List[Dict]}} (de envios_data.json).</li>
                    </ul>
                </div>
                <h4 style="margin-top:14px;">Comportamiento Detallado de ordenarTransporte</h4>
                <div class="flow-step">
                    <strong>Cómo</strong>: Parsea JSON/dict, extrae cliente/producto/cantidad/total (defaults si faltan), logs en consola, agrega envío a JSON con estado "Despachado" y fecha actual.
                </div>
                <div class="flow-step">
                    <strong>Cuándo</strong>: Invocado por Tienda o Compras/Ventas al confirmar una venta. Proceso síncrono.
                </div>
                <div class="flow-step">
                    <strong>Dónde</strong>: Historial en envios_data.json (persistencia local). No actualizaciones externas.
                </div>
                <div class="warning-box" style="margin-top:10px;">
                    <strong>⚠️ Comportamiento contra fallos:</strong> Si parse falla, retorna error. Archivo JSON se crea si no existe.
                </div>
            </div>
            <div class="section" id="persistencia">
                <h2>🔹 Persistencia y Almacenamiento</h2>
                <div class="module-card">
                    <p>Historial de envíos en <code>envios_data.json</code> (creado automáticamente si no existe). Estructura: List[Dict] con {{'cliente': str, 'producto': str, 'cantidad': int, 'total': int, 'estado': str, 'fecha_envio': str}}.</p>
                    <ul>
                        <li><strong>cargar_envios()</strong>: Lee JSON o crea vacío.</li>
                        <li><strong>guardar_envios(envios)</strong>: Sobrescribe JSON con indent=4.</li>
                    </ul>
                </div>
            </div>
            <div class="section" id="arquitectura">
                <h2>Arquitectura del Sistema (Integración)</h2>
                <pre style="background:#1e1e1e;color:#4ec9b0;padding:12px;border-radius:8px;"> 
+-------------------+      +-------------------------+
| Tienda / Compras  | ---> | Transportador (7000/rpc)|
| (órdenes envío)   |      | (registro y confirmación)|
+-------------------+      +-------------------------+
                
Protocolos: XML-RPC sobre HTTP (payload JSON/dict). Sin llamadas salientes.
                </pre>
                <div class="warning-box">
                    <strong>⚠️ Seguridad y red:</strong> Este entorno NO implementa autenticación ni cifrado. Producción requiere TLS, autenticación mutua o VPN y control de acceso de red.
                </div>
            </div>
            <div class="section" id="instalacion">
                <h2>Instalación y Puesta en Marcha</h2>
                <ol>
                    <li><strong>Iniciar transportador.py:</strong> python transportador.py (escucha en 7000).</li>
                    <li><strong>Acceder a doc:</strong> http://{ip}:{PUERTO_DOCUMENTACION}.</li>
                </ol>
                <div class="warning-box" style="margin-top:8px;">
                    <strong>⚠️ Firewall:</strong> Abra el puerto 7000 para llamadas RPC internas.
                </div>
                <h4 style="margin-top:12px;">Recomendaciones adicionales</h4>
                <ul>
                    <li>Agregar logging más robusto para producción.</li>
                    <li>Implementar backups de envios_data.json.</li>
                    <li>Integrar con servicios de logística reales si necesario.</li>
                </ul>
            </div>
            <div class="section">
                <h2>Ejemplo Mínimo (Cliente Python) — ordenarTransporte</h2>
                <div class="code-block">
# Cliente simple para ordenar transporte
import xmlrpc.client
import json
server = xmlrpc.client.ServerProxy('http://{ip}:7000/rpc', allow_none=True)
data = {{'cliente': 'Ana', 'producto': 'Silla Ergonómica', 'cantidad': 2, 'total': 700000}}
resp = server.ordenarTransporte(json.dumps(data))
print(resp)
                </div>
            </div>
            <div class="section">
                <h2>Solución de Problemas</h2>
                <table>
                    <tr><th>Error</th><th>Causa</th><th>Solución</th></tr>
                    <tr><td>Method "ordenarTransporte" not supported</td><td>URL o método incorrecto</td><td>Usar URL correcta[](http://{ip}:7000/rpc) y método exacto.</td></tr>
                    <tr><td>JSONDecodeError en carga</td><td>Archivo corrupto</td><td>Retorna lista vacía; revisar/backupear envios_data.json.</td></tr>
                    <tr><td>Address already in use</td><td>Puerto 7000 ocupado</td><td>Cerrar proceso previo o cambiar port en código.</td></tr>
                    <tr><td>ValueError: Formato no reconocido</td><td>Input no es str/dict</td><td>Enviar json_data como string JSON o dict.</td></tr>
                    <tr><td>AttributeError: 'NoneType' object has no attribute 'encode'</td><td>La función crear_pagina_principal() devuelve None, posiblemente por falta del 'return html' al final de la función o indentación incorrecta.</td><td>Asegúrate de que la función crear_pagina_principal() tenga 'return html' al final, con la indentación correcta (al nivel de la función, no dentro del f-string).</td></tr>
                </table>
            </div>
            <div class="section">
                <h2>Glosario Corto</h2>
                <table>
                    <tr><th>Término</th><th>Significado</th></tr>
                    <tr><td>Orden de Envío</td><td>Solicitud de transporte desde Tienda/Compras (JSON con datos pedido).</td></tr>
                    <tr><td>Persistencia Local</td><td>Almacenamiento en JSON para historial de envíos (no distribuido).</td></tr>
                </table>
            </div>
            <div class="section">
                <h2>Advertencias Finales</h2>
                <div class="warning-box">
                    • Este servidor de documentación NO implementa autenticación. No lo exponga a redes públicas.
                    <br>• Para entornos reales, implemente TLS, autenticación y control de acceso por IP/ACL.
                    <br>• El módulo simula transporte; en producción, integre con APIs de logística.
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
            try:
                html = crear_pagina_principal()
                if html is None:
                    print("Warning: crear_pagina_principal returned None")
                    html = "<h1>Error: Página no generada</h1>"
                self.wfile.write(html.encode('utf-8'))
            except Exception as e:
                print(f"Error al generar o enviar la página: {e}")
                self.wfile.write("<h1>Error interno del servidor</h1>".encode('utf-8'))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        ip_cliente = self.client_address[0]
        print(f"📡 Petición desde {ip_cliente}: {args[0]}")

def iniciar_servidor_documentacion():
    ip = obtener_ip_local()
    puerto = PUERTO_DOCUMENTACION

    print("\n" + "="*70)
    print("📚 SERVIDOR DE DOCUMENTACIÓN - TRANSPORTADOR INICIADO")
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