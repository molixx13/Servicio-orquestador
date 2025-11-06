"""
Servicio: Atención a Proveedores
Autor: Molixx13
Descripción:
------------
Servicio XML-RPC que recibe requerimientos desde el módulo Inventario,
genera las compras correspondientes a proveedores y notifica al módulo
de Compras/Ventas para su registro y envío de factura a Contabilidad.

IMPORTANTE: NO actualiza el inventario directamente. 
Contabilidad es el ÚNICO responsable de actualizar el inventario.
"""

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import json
import os
import socket
from datetime import datetime

# ===========================================================
# CONFIGURACIÓN DE RED Y ARCHIVOS
# ===========================================================
hostIP = str(socket.gethostbyname(socket.gethostname()))
port = 7005

# URL de otros módulos
COMPRAS_VENTAS_RPC_URL = "http://192.168.100.233:9000/rpc"
CONTABILIDAD_RPC_URL = "http://25.21.199.213:10010"

# Archivo local para registrar compras simuladas
DATA_FILE = "compras_proveedores.json"

# ===========================================================
# FUNCIONES AUXILIARES
# ===========================================================
def cargar_compras():
    """Carga el historial local de compras realizadas a proveedores."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_compras(compras):
    """Guarda las compras en disco."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(compras, f, indent=4, ensure_ascii=False)

def _parse_rpc_response(resp):
    """Acepta respuesta que puede ser dict/struct o JSON string."""
    try:
        if isinstance(resp, str):
            return json.loads(resp)
        return resp
    except Exception as e:
        return {"error_parse": str(e), "raw": resp}

def banner_inicio():
    """Imprime información del servidor."""
    print("=" * 70)
    print("🏢 SERVIDOR ATENCIÓN A PROVEEDORES INICIADO")
    print("=" * 70)
    print(f"📍 IP de esta máquina: {hostIP}")
    print(f"🔌 Puerto: {port}")
    print(f"🌐 URL RPC: http://{hostIP}:{port}/rpc")
    print(f"📡 Protocolo: XML-RPC")
    print("=" * 70)
    print("\n📋 MÉTODOS DISPONIBLES:")
    print("   • procesarRequerimiento(json_data)")
    print("      └─ Recibe requerimientos desde Inventario")
    print("   • listarCompras()")
    print("      └─ Devuelve compras realizadas a proveedores")
    print("=" * 70)
    print("\n⚡ MEJORAS:")
    print("   ✓ NO actualiza inventario directamente")
    print("   ✓ Contabilidad maneja toda la lógica de inventario")
    print("   ✓ Sin duplicaciones de stock")
    print("=" * 70)
    print("\n⏳ Esperando llamadas RPC...\n")

# ===========================================================
# CLASE PRINCIPAL
# ===========================================================
class ServidorAtencionProveedores:
    """Simula la atención y abastecimiento con proveedores externos."""

    def __init__(self):
        self.compras_rpc = xmlrpc.client.ServerProxy(COMPRAS_VENTAS_RPC_URL, allow_none=True)

    def procesarRequerimiento(self, json_data):
        """
        Recibe un requerimiento desde Inventario y simula la compra al proveedor.
        Envía la orden a Compras/Ventas.
        
        IMPORTANTE: NO actualiza el inventario directamente.
        Contabilidad es el responsable de actualizar el inventario.
        """
        try:
            data = json.loads(json_data)
            productos = data.get("productos", [])
            proveedor = data.get("proveedor", "ProveedorXYZ")

            print("=" * 70)
            print("📦 REQUERIMIENTO RECIBIDO DESDE INVENTARIO")
            print("=" * 70)
            print(json.dumps(data, indent=4, ensure_ascii=False))
            print("=" * 70)

            if not productos:
                return {"status": "error", "mensaje": "Sin productos en el requerimiento"}

            # Registrar compra local
            compras = cargar_compras()
            compra_id = f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            nueva_compra = {
                "id": compra_id,
                "proveedor": proveedor,
                "productos": productos,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            compras.append(nueva_compra)
            guardar_compras(compras)

            print("🪑 Productos solicitados:")
            for p in productos:
                print(f"   • {p['nombre']} x{p['cantidad']}")

            total = sum(p["cantidad"] * 100000 for p in productos)  # Valor simulado

            # ===========================================================
            # 📤 Enviar orden de compra a Compras/Ventas
            # ===========================================================
            print(f"\n📡 Enviando orden de compra a Compras/Ventas ({COMPRAS_VENTAS_RPC_URL}) ...")
            try:
                compras_rpc = xmlrpc.client.ServerProxy(COMPRAS_VENTAS_RPC_URL, allow_none=True)

                # Probar conexión
                ping_raw = compras_rpc.consultar_compras()
                ping = _parse_rpc_response(ping_raw)
                total_compras = (
                    ping.get("total", 0)
                    if isinstance(ping, dict)
                    else len(ping) if isinstance(ping, list)
                    else 0
                )
                print(f"✅ Conexión confirmada. Compras registradas actualmente: {total_compras}")

                # Enviar solicitud
                payload = {
                    "proveedor": proveedor,
                    "productos": [p["nombre"] for p in productos],
                    "total": total
                }
                respuesta_raw = compras_rpc.registrar_compra(json.dumps(payload))
                respuesta = _parse_rpc_response(respuesta_raw)

                print("✅ Orden de compra enviada a Compras/Ventas.")
                print(f"📥 Respuesta recibida:\n{json.dumps(respuesta, indent=4, ensure_ascii=False)}")

                # Verificar estado de Contabilidad
                estado_cont = respuesta.get("respuesta_contabilidad", {})
                if isinstance(estado_cont, dict):
                    if estado_cont.get("status") == "ok":
                        print("\n✅ Contabilidad procesó la compra correctamente")
                        print("   └─ Inventario actualizado automáticamente por Contabilidad")
                    else:
                        print(f"\n⚠️ Contabilidad no respondió OK: {estado_cont.get('detalle', 'desconocido')}")

            except Exception as e:
                print(f"❌ Error al contactar Compras/Ventas: {e}")
                respuesta = {"status": "pendiente", "detalle": str(e)}

            # ===========================================================
            # ⬇️ CAMBIO CRÍTICO: NO actualizar inventario aquí
            # Contabilidad ya lo hizo (o lo hará en segundo plano)
            # ===========================================================
            print("\nℹ️ Inventario actualizado por Contabilidad (responsabilidad única)")
            print("   └─ NO se realiza actualización duplicada desde este módulo")

            # ===========================================================
            # 🧾 Respuesta final
            # ===========================================================
            return {
                "status": "ok",
                "mensaje": "Requerimiento procesado correctamente",
                "compra_id": compra_id,
                "respuesta_compras": respuesta
            }

        except Exception as e:
            print(f"❌ Error en procesarRequerimiento: {e}")
            return {"status": "error", "detalle": str(e)}

    def listarCompras(self):
        """Devuelve las compras registradas a proveedores."""
        compras = cargar_compras()
        return {"total": len(compras), "data": compras}

# ===========================================================
# CONFIGURACIÓN DE RUTA /rpc
# ===========================================================
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/rpc',)

# ===========================================================
# SERVIDOR PRINCIPAL
# ===========================================================
if __name__ == "__main__":
    server = SimpleXMLRPCServer(
        (hostIP, port),
        requestHandler=RequestHandler,
        allow_none=True,
        logRequests=True
    )
    server.register_instance(ServidorAtencionProveedores())
    banner_inicio()
    server.serve_forever()
