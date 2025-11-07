"""
Servidor de Documentación - Atención a Proveedores (Sistema Orquestado de Tienda de Muebles)
Autor: Molixx13
Fecha: 2025-11-07
Descripción:
---------------
Servidor HTTP que muestra la documentación técnica detallada del módulo Atención a Proveedores.
Basado en el servidor de documentación para Compras/Ventas, adaptado para reflejar con precisión
el flujo y comportamiento de atencion_provedores.py. Incluye descripciones de métodos RPC,
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

PUERTO_DOCUMENTACION = 8092  # Cambiado para evitar conflictos de puerto

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
    Crea la página HTML principal con documentación técnica detallada para Atención a Proveedores.
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
    <title>Documentación Técnica - Atención a Proveedores (Sistema Orquestado)</title>
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
            <h1>🏢 Módulo de Atención a Proveedores</h1>
            <p>Documentación Técnica Detallada — Sistema Orquestado de Tienda de Muebles</p>
            <p style="font-size:0.9em; margin-top:6px;">Autor: Molixx13 — Fecha: 2025-11-07 — Versión: 2.0</p>
        </div>

        <div class="info-bar">
            <div class="info-item"><div class="label">📍 IP del Servidor</div><div class="value">{ip}</div></div>
            <div class="info-item"><div class="label">🔌 Puerto Doc</div><div class="value">{PUERTO_DOCUMENTACION}</div></div>
            <div class="info-item"><div class="label">🔌 Puerto RPC</div><div class="value">7005</div></div>
            <div class="info-item"><div class="label">🌐 Protocolo</div><div class="value">XML-RPC (ruta: /rpc)</div></div>
        </div>

        <div class="content">
            <div class="section">
                <h2>📑 Índice Rápido</h2>
                <p>Este módulo gestiona relaciones con proveedores, procesa requerimientos de reabastecimiento desde Inventario, simula compras y notifica a Compras/Ventas. NO actualiza inventario directamente (delegado a Contabilidad para responsabilidad única).</p>
            </div>

            <div class="section" id="descripcion">
                <h2>🔹 Descripción General</h2>
                <div class="module-card">
                    <h3>Responsabilidades Principales</h3>
                    <ul>
                        <li>Recibir requerimientos de productos con bajo stock desde Inventario.</li>
                        <li>Simular gestión de compras con proveedores externos (e.g., ProveedorXYZ por defecto).</li>
                        <li>Notificar compras al módulo Compras/Ventas para registro contable.</li>
                        <li>Mantener historial local de compras en <code>compras_proveedores.json</code>.</li>
                        <li><strong>Importante:</strong> NO actualiza inventario (evita duplicación; Contabilidad es responsable única).</li>
                    </ul>

                    <h4 style="margin-top:12px;">Arquitectura y Flujo Típico</h4>
                    <p>Servidor XML-RPC escuchando en /rpc. Comunicación unidireccional: Inventario → Proveedores → Compras/Ventas → Contabilidad → Inventario (actualización).</p>
                    <ol>
                        <li>Inventario detecta stock bajo y llama a <code>procesarRequerimiento()</code>.</li>
                        <li>Registra compra local en JSON.</li>
                        <li>Notifica a Compras/Ventas vía <code>registrar_compra</code>.</li>
                        <li>Compras/Ventas notifica a Contabilidad.</li>
                        <li>Contabilidad actualiza inventario (responsabilidad única).</li>
                    </ol>

                    <h4 style="margin-top:12px;">Mejoras vs Versión Anterior</h4>
                    <ul>
                        <li>✅ NO actualiza inventario (evita duplicación).</li>
                        <li>✅ Responsabilidad única clara.</li>
                        <li>✅ Sin llamadas redundantes.</li>
                    </ul>

                    <h4 style="margin-top:12px;">Dependencias</h4>
                    <table>
                        <tr><th>Módulo</th><th>URL</th><th>Propósito</th></tr>
                        <tr><td>Compras/Ventas</td><td>http://192.168.100.233:9000/rpc</td><td>Registro de compras</td></tr>
                        <tr><td>Contabilidad</td><td>http://25.21.199.213:10010</td><td>Referencia (no usado directamente; actualiza inventario)</td></tr>
                        <tr><td>Inventario</td><td>Indirecto</td><td>Origen de requerimientos</td></tr>
                    </table>
                </div>
            </div>

            <div class="section" id="metodos">
                <h2>🔹 Métodos RPC Expuestos</h2>
                <div class="module-card">
                    <h3>procesarRequerimiento(json_data: str) → Dict[str, Any]</h3>
                    <p>Procesa requerimiento de Inventario, simula compra, guarda localmente y notifica a Compras/Ventas.</p>
                    <h4>Argumentos</h4>
                    <ul>
                        <li><strong>json_data</strong>: JSON string con {{'origen': 'Inventario', 'productos': [{{'nombre': str, 'cantidad': int}}], 'motivo': str, 'proveedor': str (opcional)}}.</li>
                    </ul>
                    <h4>Retorno</h4>
                    <ul>
                        <li>Dict con {{'status': 'ok/error', 'mensaje': str, 'compra_id': str (COMP-YYYYMMDDHHMMSS), 'respuesta_compras': Dict}}.</li>
                    </ul>

                    <h3>listarCompras() → Dict[str, Any]</h3>
                    <p>Retorna todas las compras registradas localmente.</p>
                    <h4>Retorno</h4>
                    <ul>
                        <li>Dict con {{'total': int, 'data': List[Dict]}} (de compras_proveedores.json).</li>
                    </ul>
                </div>

                <h4 style="margin-top:14px;">Comportamiento Detallado de procesarRequerimiento</h4>
                <div class="flow-step">
                    <strong>Cómo</strong>: Parsea JSON, valida productos, genera ID compra, guarda en JSON local, calcula total simulado (cantidad * 100000), prueba conexión con Compras/Ventas (consultar_compras), envía registrar_compra con payload {{'proveedor': proveedor, 'productos': [nombres de productos], 'total': total}}.
                </div>

                <div class="flow-step">
                    <strong>Cuándo</strong>: Invocado por Inventario al detectar bajo stock. Proceso síncrono, pero con manejo de errores para no bloquear.
                </div>

                <div class="flow-step">
                    <strong>Dónde</strong>: Historial en compras_proveedores.json (persistencia local). Notificación a Compras/Ventas (192.168.100.233:9000/rpc). Verifica respuesta de Contabilidad indirectamente vía respuesta_compras.
                </div>

                <div class="warning-box" style="margin-top:10px;">
                    <strong>⚠️ Comportamiento contra fallos:</strong> Si Compras/Ventas falla, la compra se guarda localmente y se retorna status="ok" con respuesta_compras={{'status': 'pendiente'}}. NO actualiza inventario aquí.
                </div>
            </div>

            <div class="section" id="persistencia">
                <h2>🔹 Persistencia y Almacenamiento</h2>
                <div class="module-card">
                    <p>Historial de compras en <code>compras_proveedores.json</code> (creado automáticamente si no existe). Estructura: List[Dict] con {{'id': str, 'proveedor': str, 'productos': list, 'fecha': str}}.</p>
                    <ul>
                        <li><strong>cargar_compras()</strong>: Lee JSON o crea vacío.</li>
                        <li><strong>guardar_compras(compras)</strong>: Sobrescribe JSON con indent=4.</li>
                    </ul>
                </div>
            </div>

            <div class="section" id="arquitectura">
                <h2>Arquitectura del Sistema (Integración)</h2>
                <pre style="background:#1e1e1e;color:#4ec9b0;padding:12px;border-radius:8px;"> 
+-------------+      +----------------------+        +-----------------------+        +-------------+
| Inventario  | ---> | AtenciónProveedores  | -----> | Compras/Ventas (9000) | -----> | Contabilidad|
| (bajo stock)|      | (7005/rpc)           |        | (orquestador)         |        | (10010)     |
+-------------+      +----------------------+        +-----------------------+        +-------------+
                                                     |                                     ^
                                                     |                                     |
                                                     +-------------------------------------+
                                                                   (Contabilidad actualiza inventario)
                
Protocolos: XML-RPC sobre HTTP (payload JSON). Comunicación unidireccional para evitar ciclos.
                </pre>

                <div class="warning-box">
                    <strong>⚠️ Seguridad y red:</strong> Este entorno NO implementa autenticación ni cifrado. Producción requiere TLS, autenticación mutua o VPN y control de acceso de red.
                </div>
            </div>

            <div class="section" id="instalacion">
                <h2>Instalación y Puesta en Marcha</h2>
                <ol>
                    <li><strong>Iniciar dependencias:</strong> Compras/Ventas (9000), Contabilidad (10010).</li>
                    <li><strong>Ejecutar atencion_provedores.py:</strong> python atencion_provedores.py (escucha en 7005).</li>
                    <li><strong>Acceder a doc:</strong> http://{ip}:{PUERTO_DOCUMENTACION}.</li>
                </ol>

                <div class="warning-box" style="margin-top:8px;">
                    <strong>⚠️ Firewall:</strong> Abra el puerto 7005 para llamadas RPC internas.
                </div>

                <h4 style="margin-top:12px;">Recomendaciones adicionales</h4>
                <ul>
                    <li>Implementar timeouts en conexiones RPC y reintentos para robustez.</li>
                    <li>Agregar backup periódico de compras_proveedores.json.</li>
                    <li>Monitorear logs para requerimientos procesados y errores en notificaciones.</li>
                </ul>
            </div>

            <div class="section">
                <h2>Ejemplo Mínimo (Cliente Python) — procesarRequerimiento</h2>
                <div class="code-block">
# Cliente simple para procesar un requerimiento
import xmlrpc.client
import json

server = xmlrpc.client.ServerProxy('http://{ip}:7005/rpc', allow_none=True)
data = {{'origen': 'Inventario', 'productos': [{{'nombre': 'Mesa', 'cantidad': 10}}], 'motivo': 'Bajo stock'}}
resp = server.procesarRequerimiento(json.dumps(data))
print(resp)
                </div>
                <p>Nota: Asegúrate de usar la IP correcta del servidor de Atención a Proveedores (e.g., 192.168.100.233) y el puerto 7005. El error mostrado ocurre porque se usó una URL incorrecta (25.21.199.213:8010, que es probablemente para Inventario o Contabilidad).</p>
            </div>

            <div class="section">
                <h2>Solución de Problemas</h2>
                <table>
                    <tr><th>Error</th><th>Causa</th><th>Solución</th></tr>
                    <tr><td>Error al contactar Compras/Ventas</td><td>Servicio caído o red</td><td>Ver logs; compra se guarda local; reintentar manualmente si necesario.</td></tr>
                    <tr><td>JSONDecodeError en carga</td><td>Archivo corrupto</td><td>Retorna lista vacía; revisar/backupear compras_proveedores.json.</td></tr>
                    <tr><td>Address already in use</td><td>Puerto ocupado</td><td>Cerrar proceso previo o cambiar puerto en código (e.g., PUERTO_DOCUMENTACION).</td></tr>
                    <tr><td>Sin productos en requerimiento</td><td>Input inválido</td><td>Retorna {{'status': 'error'}}; validar en llamador (Inventario).</td></tr>
                    <tr><td>Method "procesarRequerimiento" not supported</td><td>URL de servidor incorrecta</td><td>Usar la URL correcta para Atención a Proveedores: http://192.168.100.233:7005/rpc (ajusta IP si necesario).</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Glosario Corto</h2>
                <table>
                    <tr><th>Término</th><th>Significado</th></tr>
                    <tr><td>Requerimiento</td><td>Solicitud de reabastecimiento desde Inventario (JSON con productos).</td></tr>
                    <tr><td>Responsabilidad Única</td><td>Contabilidad es el único que actualiza inventario para evitar inconsistencias.</td></tr>
                    <tr><td>Persistencia Local</td><td>Almacenamiento en JSON para historial de compras (no distribuido).</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>Advertencias Finales</h2>
                <div class="warning-box">
                    • Este servidor de documentación NO implementa autenticación. No lo exponga a redes públicas.
                    <br>• Para entornos reales, implemente TLS, autenticación y control de acceso por IP/ACL.
                    <br>• El módulo simula compras; en producción, integre APIs reales de proveedores.
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
    print("📚 SERVIDOR DE DOCUMENTACIÓN - ATENCIÓN A PROVEEDORES INICIADO")
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