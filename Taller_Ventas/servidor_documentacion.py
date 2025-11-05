"""
Módulo: servidor_documentacion
Autor: Molixx13
Descripción:
---------------
Servidor HTTP que muestra la documentación del sistema de Compras/Ventas.
Accesible desde cualquier navegador en la red local SIN autenticación.

Características:
- Documentación visual e interactiva
- Diagramas de flujo animados
- Ejemplos de código con sintaxis coloreada
- Opción de imagen de fondo personalizada del equipo
- Responsive y moderno

Uso:
----
1. (Opcional) Colocar imagen del equipo como "equipo.jpg" en la misma carpeta
2. Ejecutar: python servidor_documentacion.py
3. Desde otro PC: abrir navegador y visitar http://IP:8081
"""

import http.server
import socketserver
import socket
import os
import base64


# =========================
# CONFIGURACIÓN
# =========================

PUERTO_DOCUMENTACION = 8081  # Puerto donde correrá el servidor de documentación


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
    extensiones = ['.jpg', '.jpeg', '.png', '.gif']
    for ext in extensiones:
        archivo = f"equipo{ext}"
        if os.path.exists(archivo):
            try:
                with open(archivo, 'rb') as f:
                    img_data = f.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.png': 'image/png',
                        '.gif': 'image/gif'
                    }.get(ext, 'image/jpeg')
                    print(f"✅ Imagen del equipo cargada: {archivo}")
                    return f"data:{mime_type};base64,{img_base64}"
            except Exception as e:
                print(f"⚠️ Error cargando imagen: {e}")
    return ""


def crear_pagina_principal():
    """
    Crea la página HTML principal con documentación completa y visual.
    """
    ip = obtener_ip_local()
    imagen_equipo = cargar_imagen_equipo()
    
    # Si hay imagen, usar como fondo; si no, usar gradiente
    fondo_body = f"background-image: url('{imagen_equipo}'); background-size: cover; background-attachment: fixed; background-position: center;" if imagen_equipo else "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
    
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación Sistema Distribuido - Compras/Ventas</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            {fondo_body}
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }}
        
        /* Overlay para mejorar legibilidad si hay imagen de fondo */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, {'0.5' if imagen_equipo else '0'});
            pointer-events: none;
            z-index: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 25px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4);
            overflow: hidden;
            position: relative;
            z-index: 1;
            backdrop-filter: blur(10px);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }}
        
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            animation: fadeInDown 1s ease-out;
        }}
        
        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.95;
        }}
        
        .info-bar {{
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            padding: 25px 40px;
            border-bottom: 3px solid #667eea;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .info-item {{
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .info-item:hover {{
            transform: translateY(-5px);
        }}
        
        .info-item .label {{
            font-size: 0.95em;
            color: #6c757d;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .info-item .value {{
            font-size: 1.8em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
            animation: fadeIn 0.8s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 4px solid #667eea;
            font-size: 2.2em;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .section h2::before {{
            content: '📌';
            font-size: 1.2em;
        }}
        
        .module-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 30px;
            color: white;
            margin: 25px 0;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            transition: all 0.4s;
            position: relative;
            overflow: hidden;
        }}
        
        .module-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            transition: transform 0.5s;
        }}
        
        .module-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
        }}
        
        .module-card:hover::before {{
            transform: translate(20%, 20%);
        }}
        
        .module-card h3 {{
            font-size: 2em;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
        }}
        
        .module-card p, .module-card ul {{
            opacity: 0.95;
            line-height: 1.8;
            position: relative;
            z-index: 1;
        }}
        
        .module-card ul {{
            list-style: none;
            padding-left: 0;
            margin-top: 20px;
        }}
        
        .module-card li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
        }}
        
        .module-card li::before {{
            content: '→';
            position: absolute;
            left: 0;
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .code-block {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 25px;
            border-radius: 12px;
            font-family: 'Consolas', 'Monaco', monospace;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            position: relative;
        }}
        
        .code-block::before {{
            content: 'Python';
            position: absolute;
            top: 8px;
            right: 15px;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 5px;
            font-size: 0.75em;
            font-weight: bold;
        }}
        
        .code-block .keyword {{ color: #569cd6; }}
        .code-block .string {{ color: #ce9178; }}
        .code-block .function {{ color: #dcdcaa; }}
        .code-block .comment {{ color: #6a9955; }}
        
        .architecture {{
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 20px;
            padding: 35px;
            margin-top: 25px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.05);
        }}
        
        .architecture pre {{
            background: #1e1e1e;
            color: #4ec9b0;
            padding: 30px;
            border-radius: 15px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            line-height: 1.8;
            font-size: 0.95em;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .flow-diagram {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 25px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .flow-step {{
            background: linear-gradient(to right, #667eea, #764ba2);
            color: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 12px;
            position: relative;
            padding-left: 60px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s;
        }}
        
        .flow-step:hover {{
            transform: translateX(10px);
        }}
        
        .flow-step::before {{
            content: attr(data-step);
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(255,255,255,0.3);
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
        }}
        
        .flow-arrow {{
            text-align: center;
            color: #667eea;
            font-size: 2em;
            margin: 10px 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-radius: 12px;
            overflow: hidden;
        }}
        
        th, td {{
            padding: 18px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        tr {{
            background: white;
            transition: all 0.3s;
        }}
        
        tr:hover {{
            background: #f8f9fa;
            transform: scale(1.01);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .feature-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .feature-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .feature-card p {{
            color: #555;
            line-height: 1.7;
        }}
        
        .warning-box {{
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .success-box {{
            background: #d4edda;
            border-left: 5px solid #28a745;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .info-box {{
            background: #d1ecf1;
            border-left: 5px solid #17a2b8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .footer {{
            background: #2d3748;
            color: white;
            text-align: center;
            padding: 40px 20px;
            position: relative;
        }}
        
        .footer p {{
            margin: 10px 0;
        }}
        
        .nav-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 35px;
            border-radius: 30px;
            text-decoration: none;
            margin: 10px;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .nav-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        }}
        
        /* Animaciones */
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .section h2 {{ font-size: 1.6em; }}
            .content {{ padding: 20px; }}
            .info-bar {{ grid-template-columns: 1fr; }}
        }}
        
        /* Scroll suave */
        html {{
            scroll-behavior: smooth;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🏢 Sistema Distribuido de Compras y Ventas</h1>
                <p>Documentación Técnica Completa e Interactiva</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Universidad Minuto de Dios - 2025</p>
            </div>
        </div>
        
        <div class="info-bar">
            <div class="info-item">
                <div class="label">📍 IP del Servidor</div>
                <div class="value">{ip}</div>
            </div>
            <div class="info-item">
                <div class="label">🔌 Puerto</div>
                <div class="value">{PUERTO_DOCUMENTACION}</div>
            </div>
            <div class="info-item">
                <div class="label">📚 Módulos</div>
                <div class="value">3</div>
            </div>
            <div class="info-item">
                <div class="label">🌐 Protocolo</div>
                <div class="value">RPC</div>
            </div>
        </div>
        
        <div class="content">
            <!-- ÍNDICE RÁPIDO -->
            <div class="section">
                <h2>📑 Índice Rápido</h2>
                <div class="features-grid">
                    <a href="#modulo1" class="nav-button">Compras/Ventas</a>
                    <a href="#modulo2" class="nav-button">Atención Proveedores</a>
                    <a href="#arquitectura" class="nav-button">Arquitectura</a>
                    <a href="#instalacion" class="nav-button">Instalación</a>
                </div>
            </div>
            
            <!-- MÓDULO 1: COMPRAS/VENTAS -->
            <div class="section" id="modulo1">
                <h2>Módulo 1: Compras/Ventas (Servidor RPC)</h2>
                
                <div class="info-box">
                    <strong>🎯 Rol Principal:</strong> Este módulo actúa como el <strong>orquestador central</strong> del sistema.
                    Coordina todas las operaciones entre clientes, proveedores, contabilidad e inventario.
                </div>
                
                <div class="module-card">
                    <h3>🛒 artefacto_compras_ventas.py</h3>
                    <p><strong>Puerto:</strong> 9000</p>
                    <p><strong>Tipo:</strong> Servidor RPC (escucha conexiones)</p>
                    <p><strong>IP Configurada Contabilidad:</strong> 10.8.8.110:10010</p>
                    
                    <h4 style="margin-top: 25px;">📋 Funciones Expuestas vía RPC:</h4>
                    <ul>
                        <li><strong>registrar_venta(cliente, productos, total)</strong><br>
                        <em>Registra una venta de cliente y solicita factura a Contabilidad</em></li>
                        
                        <li><strong>registrar_compra(proveedor, productos, total)</strong><br>
                        <em>Registra compra a proveedor y envía factura a Contabilidad</em></li>
                        
                        <li><strong>obtener_ip_local()</strong><br>
                        <em>Retorna la IP del servidor para facilitar conexiones</em></li>
                        
                        <li><strong>consultar_ventas()</strong><br>
                        <em>Retorna historial completo de ventas en formato JSON</em></li>
                        
                        <li><strong>consultar_compras()</strong><br>
                        <em>Retorna historial completo de compras en formato JSON</em></li>
                        
                        <li><strong>consultar_facturas()</strong><br>
                        <em>Retorna facturas recibidas de Contabilidad</em></li>
                    </ul>
                </div>
                
                <h3 style="margin-top: 30px;">💻 Ejemplo de Uso Real desde un cliente RCP:</h3>
                <div class="code-block">
<span class="keyword">import</span> xmlrpc.client
<span class="keyword">import</span> json

<span class="comment"># Conectar al servidor Compras/Ventas</span>
compras_ventas = xmlrpc.client.<span class="function">ServerProxy</span>(<span class="string">"http://192.168.100.233:9000"</span>)

<span class="comment"># Registrar una venta</span>
resp = compras_ventas.<span class="function">registrar_venta</span>(
    <span class="string">"Carlos Lopez"</span>,
    [<span class="string">"Silla Ejecutiva Ergonómica"</span>],
    350000
)

<span class="comment"># venta_json = json.dumps(venta, ensure_ascii=False)</span>

<span class="keyword">print</span>(resp)
                </div>
                
                <h3 style="margin-top: 30px;">🔄 Flujo de una Venta (Paso a Paso):</h3>
                <div class="flow-diagram">
                    <div class="flow-step" data-step="1">
                        <strong>Cliente realiza compra</strong><br>
                        El cliente selecciona productos en la tienda física u online
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="2">
                        <strong>Tienda llama a registrar_venta()</strong><br>
                        Envía datos: cliente, productos, total vía RPC
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="3">
                        <strong>Compras/Ventas registra localmente</strong><br>
                        Guarda la venta en diccionario ventas[id_venta]
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="4">
                        <strong>Solicita factura a Contabilidad</strong><br>
                        Llama a contabilidad.generarFactura() vía RPC
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="5">
                        <strong>Contabilidad genera factura</strong><br>
                        Crea factura oficial con número, fecha, etc.
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="6">
                        <strong>Recibe y almacena factura</strong><br>
                        Guarda factura en facturas[id_venta]
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="7">
                        <strong>Retorna confirmación a Tienda</strong><br>
                        Envía JSON con venta, factura y estado
                    </div>
                </div>
                
                <h3 style="margin-top: 30px;">⚙️ Configuración del Módulo:</h3>
                <table>
                    <tr>
                        <th>Parámetro</th>
                        <th>Valor Actual</th>
                        <th>Descripción</th>
                        <th>Línea Código</th>
                    </tr>
                    <tr>
                        <td><code>IP_CONTABILIDAD</code></td>
                        <td>10.8.8.110</td>
                        <td>IP donde corre el servidor de Contabilidad</td>
                        <td>42</td>
                    </tr>
                    <tr>
                        <td><code>PUERTO_CONTABILIDAD</code></td>
                        <td>10010</td>
                        <td>Puerto del servicio RPC de Contabilidad</td>
                        <td>43</td>
                    </tr>
                    <tr>
                        <td><code>PUERTO_COMPRAS_VENTAS</code></td>
                        <td>9000</td>
                        <td>Puerto donde este servidor escucha</td>
                        <td>46</td>
                    </tr>
                </table>
                
                <div class="warning-box">
                    <strong>⚠️ Importante:</strong> Si Contabilidad no está disponible, el sistema continúa funcionando pero las ventas quedan sin factura. 
                    Esto está diseñado así para no interrumpir las operaciones del negocio.
                </div>
            </div>
            
            <!-- MÓDULO 2: ATENCIÓN PROVEEDORES -->
            <div class="section" id="modulo2">
                <h2>Módulo 2: Atención Proveedores (Cliente RPC)</h2>
                
                <div class="info-box">
                    <strong>🎯 Rol Principal:</strong> Gestiona la recepción de mercancía de proveedores. 
                    Es un <strong>cliente RPC</strong> que se conecta a Compras/Ventas para registrar las entregas.
                </div>
                
                <div class="module-card">
                    <h3>🏢 cliente_atencion_proveedores.py</h3>
                    <p><strong>Tipo:</strong> Cliente RPC (NO es servidor, solo se conecta)</p>
                    <p><strong>Conecta a:</strong> Compras/Ventas en puerto 9000</p>
                    <p><strong>Interfaz:</strong> Menú interactivo por consola</p>
                    
                    <h4 style="margin-top: 25px;">📋 Funciones Principales:</h4>
                    <ul>
                        <li><strong>registrar_entrega_proveedor()</strong><br>
                        <em>Registra entrega de mercancía y llama a Compras/Ventas vía RPC</em></li>
                        
                        <li><strong>listar_proveedores()</strong><br>
                        <em>Muestra todos los proveedores registrados en el sistema</em></li>
                        
                        <li><strong>listar_entregas()</strong><br>
                        <em>Muestra historial completo de entregas recibidas</em></li>
                        
                        <li><strong>verificar_conexion()</strong><br>
                        <em>Verifica que Compras/Ventas esté disponible</em></li>
                        
                        <li><strong>menu_interactivo()</strong><br>
                        <em>Interfaz de usuario amigable por consola</em></li>
                    </ul>
                </div>
                
                <h3 style="margin-top: 30px;">🔄 Flujo de Recepción de Mercancía:</h3>
                <div class="flow-diagram">
                    <div class="flow-step" data-step="1">
                        <strong>Proveedor entrega mercancía</strong><br>
                        Llega camión con productos al almacén de la empresa
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="2">
                        <strong>Empleado verifica productos</strong><br>
                        Revisa cantidad, calidad y factura del proveedor
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="3">
                        <strong>Ingresa datos en el sistema</strong><br>
                        Usa menú interactivo: código proveedor, productos, total
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="4">
                        <strong>Sistema registra localmente</strong><br>
                        Guarda entrega en diccionario entregas_recibidas[id]
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="5">
                        <strong>Llama a Compras/Ventas vía RPC</strong><br>
                        servidor.registrar_compra(proveedor, productos, total)
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="6">
                        <strong>Compras/Ventas procesa compra</strong><br>
                        Registra y envía factura a Contabilidad
                    </div>
                    <div class="flow-arrow">↓</div>
                    <div class="flow-step" data-step="7">
                        <strong>Confirmación al empleado</strong><br>
                        Muestra mensaje de éxito con ID de compra
                    </div>
                </div>
                
                <h3 style="margin-top: 30px;">👥 Proveedores Registrados:</h3>
                <table>
                    <tr>
                        <th>Código</th>
                        <th>Nombre</th>
                        <th>Productos que Suministra</th>
                    </tr>
                    <tr>
                        <td><strong>PROV001</strong></td>
                        <td>Maderera El Roble</td>
                        <td>madera, tablones, MDF, aglomerado</td>
                    </tr>
                    <tr>
                        <td><strong>PROV002</strong></td>
                        <td>Fábrica de Tapizados Premium</td>
                        <td>tela, cuero, espuma, resortes</td>
                    </tr>
                    <tr>
                        <td><strong>PROV003</strong></td>
                        <td>Herrajes y Accesorios SA</td>
                        <td>tornillos, bisagras, manijas, patas metálicas</td>
                    </tr>
                    <tr>
                        <td><strong>PROV004</strong></td>
                        <td>Pinturas y Acabados Ltda</td>
                        <td>barniz, pintura, laca, sellador</td>
                    </tr>
                </table>
            </div>
            
            <!-- ARQUITECTURA DEL SISTEMA -->
            <div class="section" id="arquitectura">
                <h2>Arquitectura del Sistema Distribuido</h2>
                
                <div class="info-box">
                    <strong>🏗️ Sistema de 3 Capas:</strong> Cliente → Middleware → Backend<br>
                    Cada módulo puede ejecutarse en una computadora diferente conectadas por red local.
                </div>
                
                <div class="architecture">
                    <h3 style="color: #667eea; margin-bottom: 20px;">Diagrama de Componentes:</h3>
                    <pre>
┌─────────────────────────────────────────────────────────────────┐
│               🌐 SISTEMA DISTRIBUIDO RPC/HTTP/JSON              │
│                      Universidad Minuto de Dios                 │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
                    │   👤 Cliente │ (Usuario final)
                    │    físico    │
                    └──────┬───────┘
                           │ compra/usa
                           ↓
            ┌─────────────────────────┐
            │    🏪 Tienda           │ (Cliente RPC)
            │    Módulo de Ventas     │
            └──────────┬──────────────┘
                       │
                       │ RPC: registrar_venta(cliente, productos, total)
                       │ HTTP POST → XML-RPC
                       │ Puerto: 9000
                       ↓
    ┌──────────────────────────────────────────────┐
    │   🛒 COMPRAS/VENTAS (Puerto 9000)           │
    │   • Servidor RPC Principal                   │
    │   • IP: 10.8.8.110                          │
    │                                              │
    │   Funciones:                                 │
    │   • registrar_venta()  ← Desde Tienda       │
    │   • registrar_compra() ← Desde Atención     │
    │   • consultar_*()                            │
    └──────┬────────────────────────┬──────────────┘
           │                        │
           │ generarFactura()       │ recibirFactura()
           │ RPC                    │ RPC
           │                        │
           ↓                        ↓
    ┌──────────────────────────────────────────────┐
    │   📊 CONTABILIDAD (Puerto 10010)            │
    │   • Genera facturas oficiales                │
    │   • IP: 10.8.8.110                          │
    │                                              │
    │   Funciones:                                 │
    │   • generarFactura(json_data)                │
    │   • recibirFactura(json_data)                │
    │   • listar_facturas()                        │
    └──────────────────────────────────────────────┘
           ↑
           │ registrar_compra()
           │ RPC
           │
    ┌──────────────────────────────────────────────┐
    │   🏢 ATENCIÓN PROVEEDORES                   │
    │   • Cliente RPC (NO servidor)                │
    │   • Menú interactivo por consola             │
    │                                              │
    │   Funciones:                                 │
    │   • registrar_entrega_proveedor()            │
    │   • listar_proveedores()                     │
    │   • listar_entregas()                        │
    └──────────────────────────────────────────────┘
           ↑
           │ entrega física
           │
    ┌──────────────┐
    │  🚚 Proveedor│ (Entrega mercancía)
    └──────────────┘


📡 PROTOCOLO: XML-RPC sobre HTTP/TCP-IP
📄 FORMATO DATOS: JSON (dentro de XML-RPC)
🔧 MIDDLEWARE: Python xmlrpc.server y xmlrpc.client
🌐 RED: LAN (192.168.x.x o 10.x.x.x)
                    </pre>
                </div>
                
                <h3 style="margin-top: 30px;">🔄 Comunicación Entre Módulos:</h3>
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>📡 XML-RPC</h3>
                        <p>Protocolo estándar para llamadas a procedimientos remotos. Permite ejecutar funciones en otra computadora como si fueran locales.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📄 JSON</h3>
                        <p>Formato de datos legible y fácil de parsear. Todos los mensajes entre módulos usan JSON para estructurar información.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔌 HTTP</h3>
                        <p>Capa de transporte sobre TCP/IP. XML-RPC viaja dentro de peticiones HTTP POST estándar.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🌐 Red Local</h3>
                        <p>Todos los módulos deben estar en la misma red LAN para poder comunicarse entre sí.</p>
                    </div>
                </div>
            </div>
            
            <!-- INSTALACIÓN Y USO -->
            <div class="section" id="instalacion">
                <h2>Instalación y Puesta en Marcha</h2>
                
                <div class="success-box">
                    <strong>✅ Requisitos Mínimos:</strong><br>
                    • Python 3.7 o superior<br>
                    • Conexión a red local LAN<br>
                    • Puertos 9000 y 10010 disponibles<br>
                    • Librerías estándar de Python (incluidas por defecto)
                </div>
                
                <h3 style="margin-top: 30px;">📥 Paso 1: Verificar Python</h3>
                <div class="code-block">
<span class="comment"># En la terminal/CMD, verificar versión de Python</span>
python --version

<span class="comment"># Debe mostrar: Python 3.7.x o superior</span>
<span class="comment"># Ejemplo: Python 3.11.5</span>
                </div>
                
                <h3 style="margin-top: 30px;">🚀 Paso 2: Iniciar los Servidores</h3>
                
                <div class="warning-box">
                    <strong>⚠️ Orden Importante:</strong> Debes iniciar los servidores en este orden:
                    <ol style="margin: 10px 0 0 20px; line-height: 2;">
                        <li>Primero: Contabilidad (puerto 10010)</li>
                        <li>Segundo: Compras/Ventas (puerto 9000)</li>
                        <li>Tercero: Clientes (Tienda, AtenciónProveedores)</li>
                    </ol>
                </div>
                
                <div class="flow-diagram" style="margin-top: 20px;">
                    <div class="flow-step" data-step="1">
                        <strong>Terminal 1: Iniciar Contabilidad</strong>
                        <div class="code-block" style="margin-top: 10px; background: #2d3748; padding: 10px;">
cd C:\ruta\del\proyecto
python artefacto_contabilidad.py
                        </div>
                    </div>
                    
                    <div class="flow-step" data-step="2" style="margin-top: 15px;">
                        <strong>Terminal 2: Iniciar Compras/Ventas</strong>
                        <div class="code-block" style="margin-top: 10px; background: #2d3748; padding: 10px;">
cd C:\ruta\del\proyecto
python artefacto_compras_ventas.py
                        </div>
                        <p style="margin-top: 10px; font-size: 0.9em;">
                            ✅ Verás: "⏳ Esperando llamadas RPC..."<br>
                            📍 Anota la IP que muestra, ejemplo: 10.8.8.110
                        </p>
                    </div>
                    
                    <div class="flow-step" data-step="3" style="margin-top: 15px;">
                        <strong>Terminal 3: Ejecutar Cliente AtenciónProveedores</strong>
                        <div class="code-block" style="margin-top: 10px; background: #2d3748; padding: 10px;">
cd C:\ruta\del\proyecto
python cliente_atencion_proveedores.py
                        </div>
                        <p style="margin-top: 10px; font-size: 0.9em;">
                            ✅ Verás el menú interactivo con opciones 1-5
                        </p>
                    </div>
                </div>
                
                <h3 style="margin-top: 40px;">⚙️ Paso 3: Configurar IPs (Si está en Red)</h3>
                
                <div class="info-box">
                    <strong>💡 ¿Cuándo necesitas configurar IPs?</strong><br>
                    Solo si los módulos están en <strong>computadoras diferentes</strong>. 
                    Si todo está en la misma PC, usa "localhost" y funciona automáticamente.
                </div>
                
                <h4 style="margin-top: 20px;">En Compras/Ventas (artefacto_compras_ventas.py):</h4>
                <div class="code-block">
<span class="comment"># Línea 42-43: Configurar IP de Contabilidad</span>
IP_CONTABILIDAD = <span class="string">"10.8.8.110"</span>       <span class="comment"># ← Cambiar por IP real</span>
PUERTO_CONTABILIDAD = 10010          <span class="comment"># Puerto de Contabilidad</span>
                </div>
                
                <h4 style="margin-top: 20px;">En AtenciónProveedores (cliente_atencion_proveedores.py):</h4>
                <div class="code-block">
<span class="comment"># Línea 31-32: Configurar IP de Compras/Ventas</span>
IP_COMPRAS_VENTAS = <span class="string">"10.8.8.110"</span>     <span class="comment"># ← IP donde corre Compras/Ventas</span>
PUERTO_COMPRAS_VENTAS = 9000         <span class="comment"># Puerto de Compras/Ventas</span>
                </div>
                
                <h3 style="margin-top: 40px;">🔥 Paso 4: Configurar Firewall de Windows</h3>
                
                <div class="warning-box">
                    <strong>⚠️ MUY IMPORTANTE:</strong> Si no configuras el firewall, los otros PCs NO podrán conectarse.
                </div>
                
                <table style="margin-top: 20px;">
                    <tr>
                        <th>Paso</th>
                        <th>Acción</th>
                    </tr>
                    <tr>
                        <td><strong>1</strong></td>
                        <td>Abrir <strong>Panel de Control</strong> → Sistema y Seguridad → Firewall de Windows</td>
                    </tr>
                    <tr>
                        <td><strong>2</strong></td>
                        <td>Click en <strong>Configuración avanzada</strong> (menú izquierdo)</td>
                    </tr>
                    <tr>
                        <td><strong>3</strong></td>
                        <td>Seleccionar <strong>Reglas de entrada</strong> → Click derecho → <strong>Nueva regla...</strong></td>
                    </tr>
                    <tr>
                        <td><strong>4</strong></td>
                        <td>Seleccionar <strong>Puerto</strong> → Siguiente</td>
                    </tr>
                    <tr>
                        <td><strong>5</strong></td>
                        <td>Protocolo: <strong>TCP</strong>, Puerto específico: <strong>9000</strong> → Siguiente</td>
                    </tr>
                    <tr>
                        <td><strong>6</strong></td>
                        <td>Acción: <strong>Permitir la conexión</strong> → Siguiente</td>
                    </tr>
                    <tr>
                        <td><strong>7</strong></td>
                        <td>Perfil: Marcar <strong>Privado</strong> → Siguiente</td>
                    </tr>
                    <tr>
                        <td><strong>8</strong></td>
                        <td>Nombre: <strong>"Python RPC Puerto 9000"</strong> → Finalizar</td>
                    </tr>
                    <tr>
                        <td><strong>9</strong></td>
                        <td><strong>REPETIR</strong> pasos 3-8 para puerto <strong>10010</strong> (Contabilidad)</td>
                    </tr>
                </table>
            </div>
            
            <!-- EJEMPLOS PRÁCTICOS -->
            <div class="section">
                <h2>💼 Ejemplos de Uso Prácticos</h2>
                
                <h3>Ejemplo 1: Registrar una Venta desde Python</h3>
                <div class="code-block">
<span class="keyword">import</span> xmlrpc.client
<span class="keyword">import</span> json

<span class="comment"># Conectar al servidor Compras/Ventas</span>
servidor = xmlrpc.client.<span class="function">ServerProxy</span>(<span class="string">'http://10.8.8.110:9000'</span>)

<span class="comment"># Datos de la venta</span>
cliente = <span class="string">"María González"</span>
productos = [<span class="string">"Sofá 3 puestos"</span>, <span class="string">"Mesa de centro"</span>, <span class="string">"Lámpara"</span>]
total = 2500000.0

<span class="comment"># Registrar la venta</span>
respuesta_json = servidor.<span class="function">registrar_venta</span>(cliente, productos, total)

<span class="comment"># Procesar respuesta</span>
respuesta = json.<span class="function">loads</span>(respuesta_json)

<span class="keyword">print</span>(<span class="string">"="</span>*60)
<span class="keyword">print</span>(<span class="string">f"✅ </span><span class="keyword">{{</span>respuesta['mensaje']<span class="keyword">}}</span><span class="string">"</span>)
<span class="keyword">print</span>(<span class="string">f"🆔 ID de Venta: </span><span class="keyword">{{</span>respuesta['id_venta']<span class="keyword">}}</span><span class="string">"</span>)
<span class="keyword">print</span>(<span class="string">f"👤 Cliente: </span><span class="keyword">{{</span>respuesta['venta']['cliente']<span class="keyword">}}</span><span class="string">"</span>)
<span class="keyword">print</span>(<span class="string">f"💵 Total: $</span><span class="keyword">{{</span>respuesta['venta']['total']:,.0f<span class="keyword">}}</span><span class="string">"</span>)
<span class="keyword">print</span>(<span class="string">f"📄 Factura recibida: </span><span class="keyword">{{</span>respuesta['factura_recibida']<span class="keyword">}}</span><span class="string">"</span>)

<span class="keyword">if</span> respuesta[<span class="string">'factura'</span>]:
    <span class="keyword">print</span>(<span class="string">f"📋 Número factura: </span><span class="keyword">{{</span>respuesta['factura'].get('numero_factura', 'N/A')<span class="keyword">}}</span><span class="string">"</span>)
<span class="keyword">print</span>(<span class="string">"="</span>*60)
                </div>
                
                <h3 style="margin-top: 30px;">Ejemplo 2: Usar AtenciónProveedores (Menú Interactivo)</h3>
                <div class="code-block">
<span class="comment"># Ejecutar el cliente</span>
$ python cliente_atencion_proveedores.py

<span class="comment"># Salida:</span>
============================================================
🏢 SISTEMA DE ATENCIÓN A PROVEEDORES
============================================================

1. Registrar entrega de proveedor
2. Listar proveedores
3. Ver historial de entregas
4. Verificar conexión con Compras/Ventas
5. Ver información de conexión
0. Salir

============================================================
Selecciona una opción: <span class="string">1</span>

<span class="comment"># El usuario selecciona opción 1 y sigue los pasos:</span>
Código del proveedor: <span class="string">PROV001</span>
Productos (separados por coma): <span class="string">madera, MDF</span>
Cantidades (separadas por coma): <span class="string">50, 30</span>
Total de la compra: $<span class="string">1200000</span>
Número de factura del proveedor: <span class="string">FACT-ROBLE-2025-001</span>

<span class="comment"># Sistema procesa y muestra:</span>
✅ COMPRA REGISTRADA EXITOSAMENTE EN EL SISTEMA
   ID Compra (Sistema): 1
   Mensaje: Compra registrada exitosamente.
   ✅ Factura enviada a Contabilidad
                </div>
            </div>
            
            <!-- SOLUCIÓN DE PROBLEMAS -->
            <div class="section">
                <h2>🔧 Solución de Problemas Comunes</h2>
                
                <table>
                    <tr>
                        <th>❌ Error</th>
                        <th>🔍 Causa</th>
                        <th>✅ Solución</th>
                    </tr>
                    <tr>
                        <td><code>ConnectionRefusedError</code></td>
                        <td>El servidor no está corriendo</td>
                        <td>Iniciar el servidor antes de ejecutar el cliente</td>
                    </tr>
                    <tr>
                        <td>No se conecta desde otro PC</td>
                        <td>Firewall bloqueando puerto</td>
                        <td>Abrir puertos 9000 y 10010 en Firewall de Windows</td>
                    </tr>
                    <tr>
                        <td>Factura no generada</td>
                        <td>Contabilidad no disponible</td>
                        <td>Normal - sistema tolera fallos. Verificar que Contabilidad esté corriendo</td>
                    </tr>
                    <tr>
                        <td><code>Address already in use</code></td>
                        <td>Puerto ya está ocupado</td>
                        <td>Cerrar la instancia anterior del servidor o cambiar puerto</td>
                    </tr>
                    <tr>
                        <td>IP incorrecta</td>
                        <td>Configuración errónea</td>
                        <td>Usar <code>ipconfig</code> (Windows) o <code>ifconfig</code> (Linux) para verificar IP</td>
                    </tr>
                    <tr>
                        <td>Respuesta vacía o None</td>
                        <td>Módulo destino no responde</td>
                        <td>Verificar que el servidor destino esté activo y en la IP correcta</td>
                    </tr>
                </table>
                
                <div class="warning-box" style="margin-top: 30px;">
                    <strong>💡 Consejo de Depuración:</strong><br>
                    Los servidores muestran logs en tiempo real. Observa la terminal donde corre el servidor para ver:
                    <ul style="margin: 10px 0 0 20px;">
                        <li>Peticiones recibidas</li>
                        <li>Errores de conexión</li>
                        <li>Operaciones exitosas</li>
                    </ul>
                </div>
            </div>
            
            <!-- CARACTERÍSTICAS TÉCNICAS -->
            <div class="section">
                <h2>⚡ Características Técnicas del Sistema</h2>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <h3>🔗 RPC Distribuido</h3>
                        <p>Comunicación mediante XML-RPC sobre HTTP. Permite llamar funciones en otras máquinas como si fueran locales. Protocolo estándar y robusto.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>📄 Formato JSON</h3>
                        <p>Todas las respuestas usan JSON para estructurar datos. Fácil de leer, parsear e integrar con otros sistemas. Compatible con cualquier lenguaje.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>🌐 Multi-Computadora</h3>
                        <p>Arquitectura distribuida real. Cada módulo puede ejecutarse en una PC diferente. Escalable y flexible según necesidades.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>📝 Documentación Completa</h3>
                        <p>Código documentado línea por línea con explicaciones claras. Docstrings en cada función. Ejemplos de uso incluidos.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>🛡️ Tolerante a Fallos</h3>
                        <p>Si un módulo falla, el sistema continúa operando. Manejo de errores en todas las conexiones RPC. No pierde datos locales.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>🔍 Auditable</h3>
                        <p>Funciones de consulta para reportes y auditorías. Historial completo de ventas, compras y facturas. Trazabilidad total.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>⚡ Asíncrono</h3>
                        <p>Servidores usan serve_forever() para atender múltiples clientes. No bloquea operaciones. Alta disponibilidad.</p>
                    </div>
                    
                    <div class="feature-card">
                        <h3>🔐 Separación Clara</h3>
                        <p>Cada módulo tiene responsabilidades bien definidas. Compras/Ventas NO genera facturas. Contabilidad es la única autoridad.</p>
                    </div>
                </div>
            </div>
            
            <!-- GLOSARIO -->
            <div class="section">
                <h2>📖 Glosario de Términos</h2>
                
                <table>
                    <tr>
                        <th>Término</th>
                        <th>Significado</th>
                        <th>Ejemplo</th>
                    </tr>
                    <tr>
                        <td><strong>RPC</strong></td>
                        <td>Remote Procedure Call - Llamada a procedimiento remoto</td>
                        <td>Ejecutar una función en otra computadora</td>
                    </tr>
                    <tr>
                        <td><strong>XML-RPC</strong></td>
                        <td>Protocolo RPC que usa XML como formato</td>
                        <td>Python: xmlrpc.server y xmlrpc.client</td>
                    </tr>
                    <tr>
                        <td><strong>JSON</strong></td>
                        <td>JavaScript Object Notation - Formato de datos</td>
                        <td>{{"cliente": "Juan", "total": 500000}}</td>
                    </tr>
                    <tr>
                        <td><strong>Servidor</strong></td>
                        <td>Programa que escucha y responde peticiones</td>
                        <td>Compras/Ventas en puerto 9000</td>
                    </tr>
                    <tr>
                        <td><strong>Cliente</strong></td>
                        <td>Programa que hace peticiones a un servidor</td>
                        <td>AtenciónProveedores conectándose a Compras/Ventas</td>
                    </tr>
                    <tr>
                        <td><strong>Middleware</strong></td>
                        <td>Software intermedio que coordina otros módulos</td>
                        <td>Compras/Ventas orquestando Tienda y Contabilidad</td>
                    </tr>
                    <tr>
                        <td><strong>Puerto</strong></td>
                        <td>Número que identifica un servicio en una IP</td>
                        <td>9000, 10010</td>
                    </tr>
                    <tr>
                        <td><strong>LAN</strong></td>
                        <td>Local Area Network - Red de área local</td>
                        <td>Computadoras conectadas en la misma red WiFi/Ethernet</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <h3 style="margin-bottom: 20px;">📚 Sistema de Compras y Ventas Distribuido</h3>
            <p>💻 Desarrollado como proyecto académico</p>
            <p>🎓 Universidad Minuto de Dios - Sistemas Distribuidos</p>
            <p>👨‍💻 Autor: Molixx13</p>
            <p>📅 Octubre 2025</p>
            <p style="margin-top: 20px; opacity: 0.8;">
                {'🖼️ Fondo personalizado cargado ✓' if imagen_equipo else '🎨 Usando fondo por defecto'}
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html


class SinAutenticacionHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handler HTTP que NO requiere autenticación.
    Sobrescribe do_AUTHHEAD para evitar el login.
    """
    
    def do_GET(self):
        """
        Maneja peticiones GET sin autenticación.
        """
        if self.path == '/' or self.path == '/index.html':
            # Sirve la página principal
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = crear_pagina_principal()
            self.wfile.write(html.encode('utf-8'))
        else:
            # Para otros paths, comportamiento normal
            super().do_GET()
    
    def log_message(self, format, *args):
        """
        Sobrescribe el método de logging para mostrar mensajes personalizados.
        """
        ip_cliente = self.client_address[0]
        print(f"📡 Petición desde {ip_cliente}: {args[0]}")


def iniciar_servidor_documentacion():
    """
    Inicia el servidor HTTP que sirve la documentación SIN autenticación.
    """
    ip = obtener_ip_local()
    puerto = PUERTO_DOCUMENTACION
    
    # Banner informativo
    print("\n" + "="*70)
    print("📚 SERVIDOR DE DOCUMENTACIÓN INICIADO")
    print("="*70)
    print(f"📍 IP de este servidor:  {ip}")
    print(f"🔌 Puerto:               {puerto}")
    print(f"🌐 URL de acceso:        http://{ip}:{puerto}")
    print("="*70)
    print("\n💡 CÓMO ACCEDER:")
    print(f"   1. Desde esta computadora:")
    print(f"      → http://localhost:{puerto}")
    print(f"\n   2. Desde otra computadora en la red:")
    print(f"      → http://{ip}:{puerto}")
    print("\n   ✅ NO requiere usuario ni contraseña")
    print("="*70)
    print("\n🖼️  PERSONALIZACIÓN:")
    print("   Para usar imagen de fondo personalizada:")
    print("   1. Coloca una imagen llamada 'equipo.jpg' (o .png)")
    print("   2. En la misma carpeta que este script")
    print("   3. Reinicia el servidor")
    print("   4. La imagen aparecerá como fondo de la documentación")
    print("="*70)
    
    # Verificar si hay imagen personalizada
    imagen = cargar_imagen_equipo()
    if imagen:
        print("\n✨ ¡Imagen personalizada detectada y cargada!")
    else:
        print("\n💡 Usando fondo por defecto (degradado)")
    
    print("="*70)
    print("\n⏳ Servidor corriendo. Presiona Ctrl+C para detener.\n")
    
    # Crea el servidor HTTP sin autenticación
    # '0.0.0.0' permite conexiones desde cualquier IP
    with socketserver.TCPServer(("0.0.0.0", puerto), SinAutenticacionHandler) as httpd:
        try:
            # Inicia el servidor
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