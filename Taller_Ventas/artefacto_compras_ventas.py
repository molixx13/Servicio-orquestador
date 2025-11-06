# artefacto_compras_ventas.py
"""
Módulo: artefacto_compras_ventas
Autor: Molixx13 (modificado)
Descripción:
    Servicio RPC multihilo para Compras/Ventas.
    - Registrar ventas (invocado por Tienda)
    - Registrar compras (invocado por AtenciónProveedores)
    - Enviar facturas a Contabilidad y notificar Inventario
    - Respuestas consistentes (estructuras/dicts XML-RPC)
"""

from datetime import datetime
import json
import socket
import threading
import traceback
import http.client

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xmlrpc.client

# -------------------------
# Configuración de red/servicios
# -------------------------
IP_CONTABILIDAD = "25.21.199.213"
PUERTO_CONTABILIDAD = 10010
CONTABILIDAD_RPC_URL = f"http://{IP_CONTABILIDAD}:{PUERTO_CONTABILIDAD}"

PUERTO_COMPRAS_VENTAS = 9000

# Rutas exactas (asegúrate de que los otros servicios usen /rpc o adapta aquí)
INVENTARIO_RPC_URL = "http://25.21.199.213:8010/rpc"

# -------------------------
# Timeouts y protección
# -------------------------
# Timeout global aumentado para evitar timeouts
socket.setdefaulttimeout(90)  # ⬅️ CAMBIO: 90 segundos

# Lock para proteger estructuras compartidas (thread-safe)
_lock = threading.Lock()

# -------------------------
# Estructuras en memoria
# -------------------------
ventas = {}
compras = {}
facturas = {}

# -------------------------
# Utilidades
# -------------------------
def _next_id(collection):
    with _lock:
        return len(collection) + 1

def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# ⬇️ NUEVO: Transport con timeout personalizado
class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout=90):
        super().__init__()
        self.timeout = timeout
    
    def make_connection(self, host):
        return http.client.HTTPConnection(host, timeout=self.timeout)

def _safe_serverproxy(url, timeout=90):
    """Crea ServerProxy con timeout personalizado."""
    try:
        return xmlrpc.client.ServerProxy(
            url, 
            allow_none=True,
            transport=TimeoutTransport(timeout=timeout)
        )
    except Exception as e:
        print(f"⚠️ Error creando ServerProxy({url}): {e}")
        return None

def _parse_rpc_response(resp):
    """Normaliza la respuesta de RPC: acepta dict/struct o string JSON."""
    try:
        if isinstance(resp, str):
            try:
                return json.loads(resp)
            except Exception:
                return {"raw": resp}
        else:
            return resp
    except Exception as e:
        return {"error_parse": str(e)}

# -------------------------
# Core: conexión con Contabilidad
# -------------------------
def conectar_con_contabilidad():
    url = CONTABILIDAD_RPC_URL
    return _safe_serverproxy(url, timeout=90)  # ⬅️ CAMBIO: timeout explícito

# -------------------------
# Funciones RPC expuestas
# -------------------------
def registrar_venta(cliente, productos=None, total=None):
    """
    Registra una venta realizada por la Tienda.
    Acepta:
      - (cliente:str, productos:list[str], total:float)
      - o (cliente: json-string/dict con keys cliente, productos, total)
    Retorna: dict (structure XML-RPC)
    """
    try:
        # normalizar input
        if isinstance(cliente, str) and cliente.strip().startswith("{"):
            try:
                data = json.loads(cliente)
            except Exception:
                data = {"cliente": cliente}
        elif isinstance(cliente, dict):
            data = cliente
        else:
            data = {"cliente": cliente, "productos": productos, "total": total}

        cliente_name = data.get("cliente", "Cliente desconocido")
        productos_list = data.get("productos") or ["Sin producto"]
        total_val = float(data.get("total") or 0.0)

        # proteger estructura y generar id
        venta_id = _next_id(ventas)
        venta_obj = {
            "id": venta_id,
            "cliente": cliente_name,
            "productos": productos_list,
            "total": total_val,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with _lock:
            ventas[venta_id] = venta_obj

        # Log visual
        print("\n" + "="*70)
        print("💰 NUEVA VENTA REGISTRADA")
        print("="*70)
        print(f"👤 Cliente: {cliente_name}")
        print(f"🪑 Productos: {', '.join(str(p) for p in productos_list)}")
        print(f"💵 Total: ${total_val:,.2f}")
        print(f"🆔 ID Venta: {venta_id}")
        print("="*70)

        # Solicitar factura a Contabilidad (con timeout extendido)
        factura = None
        cont = conectar_con_contabilidad()
        if cont:
            try:
                payload = {
                    "tipo_operacion": "VENTA",
                    "nombre_cliente": cliente_name,
                    "productos": [
                        {"nombre": str(p), "cantidad": 1, "precio_unit": (total_val / max(1, len(productos_list)))}
                        for p in productos_list
                    ],
                    "total": total_val
                }
                print("📞 Solicitando factura a Contabilidad (timeout: 90s)...")
                resp = cont.generarFactura(json.dumps(payload))
                factura = _parse_rpc_response(resp)
                with _lock:
                    facturas[venta_id] = factura
                print("✅ Factura recibida y almacenada.")
            except Exception as e:
                print(f"⚠️ Error solicitando factura a Contabilidad: {e}")
                traceback.print_exc()
        else:
            print("⚠️ Contabilidad no disponible. Venta registrada sin factura.")

        # Respuesta estructurada (dict) para XML-RPC
        return {
            "status": "ok",
            "mensaje": "Venta registrada exitosamente.",
            "id_venta": venta_id,
            "venta": venta_obj,
            "factura": factura
        }

    except Exception as e:
        print(f"❌ Error en registrar_venta(): {e}")
        traceback.print_exc()
        return {"status": "error", "detalle": str(e)}

def registrar_compra(proveedor=None, productos=None, total=None, data=None):
    """
    Registra una compra proveniente de AtenciónProveedores.
    Puede recibir:
      - proveedor, productos(list), total
      - data (json string or dict) con keys proveedor, productos, total
    NOTA: esta función notifica a Contabilidad (recibirFactura) ÚNICAMENTE.
    El inventario será actualizado por Contabilidad, no aquí.
    Retorna dict.
    """
    try:
        # normalizar entrada
        try:
            # Caso: string JSON
            if isinstance(proveedor, str):
                try:
                    data = json.loads(proveedor)
                except Exception:
                    # No era un JSON válido, tratar como nombre
                    data = {"proveedor": proveedor, "productos": productos or [], "total": total or 0.0}
            # Caso: dict ya decodificado
            elif isinstance(proveedor, dict):
                data = proveedor
            # Caso: parámetro data presente (string o dict)
            elif data:
                if isinstance(data, str):
                    data = json.loads(data)
            else:
                data = {"proveedor": proveedor, "productos": productos or [], "total": total or 0.0}
        except Exception as e:
            print(f"⚠️ Error interpretando datos de compra: {e}")
            data = {"proveedor": proveedor, "productos": productos or [], "total": total or 0.0}

        proveedor_name = data.get("proveedor", "Proveedor desconocido")
        productos_list = data.get("productos") or []
        total_val = float(data.get("total") or 0.0)

        # registrar compra localmente (thread-safe)
        compra_id = _next_id(compras)
        compra_obj = {
            "id": compra_id,
            "proveedor": proveedor_name,
            "productos": productos_list,
            "total": total_val,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with _lock:
            compras[compra_id] = compra_obj

        print("\n" + "="*70)
        print("🧾 NUEVA COMPRA REGISTRADA")
        print("="*70)
        print(f"🏢 Proveedor: {proveedor_name}")
        print(f"📦 Productos: {', '.join(str(p) for p in productos_list)}")
        print(f"💰 Total: ${total_val:,.2f}")
        print(f"🆔 ID Compra: {compra_id}")
        print("="*70)

        # Enviar factura a Contabilidad (ÚNICO responsable de actualizar inventario)
        respuesta_cont = None
        cont = conectar_con_contabilidad()
        if cont:
            try:
                factura_proveedor = {
                    "tipo": "COMPRA",
                    "proveedor": proveedor_name,
                    "productos": productos_list,
                    "total": total_val,
                    "compra_id": compra_id,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                print("📄 Enviando factura de compra a Contabilidad (timeout: 90s)...")
                resp = cont.recibirFactura(json.dumps(factura_proveedor))
                respuesta_cont = _parse_rpc_response(resp)
                print("✅ Contabilidad respondió:", respuesta_cont)
            except Exception as e:
                print(f"⚠️ No se pudo contactar a Contabilidad: {e}")
                traceback.print_exc()
                respuesta_cont = {"status": "pendiente", "detalle": str(e)}
        else:
            print("⚠️ Contabilidad no disponible. Marcar factura pendiente.")
            respuesta_cont = {"status": "pendiente", "detalle": "Contabilidad no disponible"}

        # ⬇️ CAMBIO CRÍTICO: NO actualizar inventario aquí
        # Contabilidad es el responsable de actualizar el inventario
        print("ℹ️ Inventario será actualizado por Contabilidad (evitando duplicación)")

        # Respuesta final (dict)
        return {
            "status": "ok",
            "mensaje": "Compra registrada exitosamente.",
            "id_compra": compra_id,
            "compra": compra_obj,
            "respuesta_contabilidad": respuesta_cont
        }

    except Exception as e:
        print(f"❌ Error en registrar_compra(): {e}")
        traceback.print_exc()
        return {"status": "error", "detalle": str(e)}

# Funciones de consulta (devuelven dicts)
def consultar_ventas():
    with _lock:
        return {"total": len(ventas), "data": ventas}

def consultar_compras():
    with _lock:
        return {"total": len(compras), "data": compras}

def consultar_facturas():
    with _lock:
        return {"total": len(facturas), "data": facturas}

# -------------------------
# Server: multihilo y RequestHandler para /rpc
# -------------------------
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/rpc",)  # Asegura que el servidor atienda en /rpc

def iniciar_servidor():
    ip = obtener_ip_local()
    puerto = PUERTO_COMPRAS_VENTAS
    host_escucha = "0.0.0.0"

    print("\n" + "="*60)
    print("🚀 SERVIDOR COMPRAS/VENTAS INICIADO")
    print("="*60)
    print(f"📍 IP: {ip}")
    print(f"🔌 Puerto: {puerto}")
    print(f"🌐 URL: http://{ip}:{puerto}/rpc")
    print(f"📡 Protocolo: XML-RPC")
    print("="*60)
    print(f"🔗 Conectando con Contabilidad → {CONTABILIDAD_RPC_URL}")
    print(f"⏱️ Timeout configurado: 90 segundos")
    print("="*60)
    print("\n⏳ Esperando llamadas RPC...\n")

    server = ThreadedXMLRPCServer((host_escucha, puerto), requestHandler=RequestHandler, allow_none=True)
    # Registrar funciones
    server.register_function(registrar_venta, "registrar_venta")
    server.register_function(registrar_compra, "registrar_compra")
    server.register_function(obtener_ip_local, "obtener_ip_local")
    server.register_function(consultar_ventas, "consultar_ventas")
    server.register_function(consultar_compras, "consultar_compras")
    server.register_function(consultar_facturas, "consultar_facturas")

    print("✅ Servidor RPC multihilo iniciado correctamente.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error fatal en el servidor: {e}\n")
        traceback.print_exc()

if __name__ == "__main__":
    iniciar_servidor()
