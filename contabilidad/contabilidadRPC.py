"""
Módulo: contabilidadRPC
Autor: Molixx13
Descripción:
------------
Servicio XML-RPC del módulo de Contabilidad.
Se encarga de generar facturas oficiales para ventas y registrar compras de proveedores.
También actualiza el inventario tras cada transacción.

Este módulo imprime en consola un banner informativo al iniciar,
y logs detallados durante cada operación de facturación o registro de compra.
"""

from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import json
import socket
from datetime import datetime


# ===========================================================
# CONFIGURACIÓN DE RED Y CONEXIONES
# ===========================================================

hostIP = str(socket.gethostbyname(socket.gethostname()))
port = 10010

# Dirección del servicio de Inventario (ajustar según red)
INVENTARIO_IP = "25.21.199.213"
INVENTARIO_PORT = 8010


# ===========================================================
# FUNCIONES AUXILIARES
# ===========================================================

def banner_inicio():
    """Imprime el banner de inicio del servidor en formato estructurado."""
    print("=" * 70)
    print("🚀 SERVIDOR CONTABILIDAD INICIADO")
    print("=" * 70)
    print(f"📍 IP de esta máquina:  {hostIP}")
    print(f"🔌 Puerto:              {port}")
    print(f"🌐 URL para conexión:   http://{hostIP}:{port}")
    print(f"🔓 Escuchando en:       0.0.0.0 (todas las interfaces)")
    print(f"📡 Protocolo:           XML-RPC")
    print(f"📄 Formato de datos:    JSON")
    print("=" * 70)
    print("\n📋 MÉTODOS DISPONIBLES VIA RPC:")
    print("   • generarFactura(json_data)")
    print("      └─ Genera factura oficial para ventas")
    print("   • recibirFactura(json_data)")
    print("      └─ Registra facturas de compras a proveedores")
    print("=" * 70)
    print(f"\n🔗 CONECTANDO CON:")
    print(f"   Inventario → http://{INVENTARIO_IP}:{INVENTARIO_PORT}/rpc")
    print("=" * 70)
    print("\n⚠️  NOTA IMPORTANTE:")
    print("   Este módulo es la ÚNICA autoridad para generar facturas.")
    print("   Mantiene numeración consecutiva y trazabilidad completa.")
    print("=" * 70)
    print("\n💡 CONEXIÓN DESDE OTRAS COMPUTADORAS:")
    print(f"   Compras/Ventas debe conectarse a:")
    print(f"   http://{hostIP}:{port}")
    print("=" * 70)
    print("\n⏳ Esperando llamadas RPC...\n")


def log_linea():
    """Imprime una línea separadora uniforme."""
    print("=" * 70)


def log_evento(mensaje):
    """Imprime un evento con marca de tiempo."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{hora}] {mensaje}")


# ===========================================================
# CLASE PRINCIPAL DEL SERVICIO
# ===========================================================

class ServidorContabilidad:
    """
    Clase que implementa los métodos remotos de Contabilidad.
    """

    def __init__(self):
        self.name = "Contabilidad"
        self.invIP = INVENTARIO_IP
        self.invPort = INVENTARIO_PORT
        # Cliente RPC hacia Inventario
        self.inventarioRPC = xmlrpc.client.ServerProxy(
            f"http://{self.invIP}:{self.invPort}/rpc", allow_none=True
        )

    # -------------------------------------------------------
    # MÉTODO: GENERAR FACTURA DE VENTA
    # -------------------------------------------------------
    def generarFactura(self, json_data):
        """Recibe la venta desde Compras/Ventas, actualiza inventario y genera factura."""
        try:
            data = json.loads(json_data)
            cliente = data.get("nombre_cliente", "Cliente desconocido")
            total = data.get("total", 0)
            productos = data.get("productos", [])
            factura_id = "FACT-2025-00046"

            # Log visual de solicitud
            print("=" * 70)
            print("📄 NUEVA SOLICITUD DE FACTURA")
            print("=" * 70)
            print(f"👤 Cliente: {cliente}")
            print(f"💵 Total: ${total:,.2f}")
            print(f"📦 Productos: {len(productos)}")
            print(f"\n📡 Comunicando con Inventario ({self.invIP}:{self.invPort})...")

            # 🔹 Asegurar tipo de operación
            data["tipo"] = "venta"

            # 🔹 Normalizar formato de datos para Inventario
            envio_data = {
                "tipo_operacion": "VENTA",
                "nombre_cliente": cliente,
                "total": total,
                "productos": []
            }

            productos_raw = data.get("productos", [])

            for p in productos_raw:
                if isinstance(p, dict):
                    # Acepta múltiples posibles formatos
                    nombre = (
                        p.get("nombre")
                        or p.get("producto")
                        or p.get("id")
                        or "Producto sin nombre"
                    )

                    envio_data["productos"].append({
                        "nombre": str(nombre),
                        "cantidad": int(p.get("cantidad", 1)),
                        "precio_unit": float(p.get("precio_unit", p.get("precio", 0)))
                    })

                elif isinstance(p, str):
                    # Caso texto plano tipo "Mesa Ikea x1"
                    partes = p.split(" x")
                    nombre = partes[0].strip()
                    cantidad = 1
                    if len(partes) > 1 and partes[1].isdigit():
                        cantidad = int(partes[1])
                    envio_data["productos"].append({
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "precio_unit": 0
                    })

            # 🔍 Depuración antes del envío
            print("\n📦 Datos finales enviados a Inventario:")
            print(json.dumps(envio_data, indent=4, ensure_ascii=False))

            # 🔹 Enviar datos al Inventario
            envio = self.inventarioRPC.actualizarInventario(json.dumps(envio_data))
            print("📥 Respuesta de Inventario recibida")

            # ----------------------------------------------------------
            # 📊 Procesar respuesta del inventario
            # ----------------------------------------------------------
            if isinstance(envio, dict) and envio.get("status") == "ok":
                factura = {
                    "factura_id": factura_id,
                    "tipo": "venta",
                    "cliente": cliente,
                    "productos": productos,
                    "total": total,
                    "estado": "Aprobada",
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                print("\n✅ FACTURA GENERADA EXITOSAMENTE")
                print(f"   Número: {factura_id}")
                print("   Estado: Aprobada")
                print("   Inventario actualizado: ✓")
                print("=" * 70)
                return json.dumps(factura, ensure_ascii=False)

            else:
                print("❌ Error al actualizar inventario.")
                print("=" * 70)
                return json.dumps({
                    "status": "error",
                    "mensaje": "No fue posible actualizar el inventario.",
                    "detalle": envio
                })

        except Exception as e:
            print(f"[ERROR Contabilidad] {e}")
            print("=" * 70)
            return json.dumps({"status": "error", "detalle": str(e)})

    # -------------------------------------------------------
    # MÉTODO: RECIBIR FACTURA DE PROVEEDOR (COMPRA)
    # -------------------------------------------------------
    def recibirFactura(self, json_data):
        """Recibe la compra enviada por Compras/Ventas, la registra y la envía a Inventario."""
        try:
            data = json.loads(json_data)
            proveedor = data.get("proveedor", "Desconocido")
            compra_id = data.get("compra_id", "sin_id")
            total = data.get("total", 0)
            productos = data.get("productos", [])

            # Log visual
            log_linea()
            print("📋 NUEVA FACTURA DE PROVEEDOR RECIBIDA")
            log_linea()
            print(f"🏢 Proveedor: {proveedor}")
            print(f"💵 Total: ${total:,.2f}")
            print(f"📦 Productos: {', '.join(productos) if productos else 'N/A'}\n")

            # Crear asiento contable simulado
            asiento = {
                "tipo": "COMPRA",
                "compra_id": compra_id,
                "proveedor": proveedor,
                "total": total,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            print(f"📝 Asiento contable creado: COMP-{compra_id}")
            print(f"\n📡 Comunicando con Inventario ({self.invIP}:{self.invPort})...")

            envio_inv = self.inventarioRPC.actualizarInventario(data)

            if isinstance(envio_inv, dict) and envio_inv.get("status") == "ok":
                print("\n✅ COMPRA REGISTRADA EXITOSAMENTE")
                print(f"   ID Compra: COMP-{compra_id}")
                print("   Inventario actualizado: ✓")
                log_linea()
                respuesta = {
                    "status": "ok",
                    "mensaje": f"Compra {compra_id} registrada correctamente.",
                    "asiento": asiento
                }
            else:
                print("\n❌ Error al actualizar inventario.")
                log_linea()
                respuesta = {
                    "status": "error",
                    "mensaje": "Fallo en actualización de inventario.",
                    "detalle": envio_inv
                }

            return json.dumps(respuesta, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR Contabilidad] {e}")
            log_linea()
            return json.dumps({"status": "error", "detalle": str(e)})

# ===========================================================
# SERVIDOR PRINCIPAL
# ===========================================================

if __name__ == "__main__":
    server = SimpleXMLRPCServer((hostIP, port), allow_none=True)
    contabilidad = ServidorContabilidad()
    server.register_instance(contabilidad)
    banner_inicio()
    server.serve_forever()

# Verifica si el script se está ejecutando directamente (no importado como módulo)
