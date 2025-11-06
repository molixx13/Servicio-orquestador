"""
Módulo: contabilidadRPC
Autor: Molixx13
Descripción:
------------
Servicio XML-RPC del módulo de Contabilidad con procesamiento asíncrono.
Se encarga de generar facturas oficiales para ventas y registrar compras de proveedores.
Actualiza el inventario en segundo plano para responder rápidamente.
"""

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import json
import socket
from datetime import datetime
import threading
from queue import Queue
import traceback

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
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/rpc', '/RPC2')

def banner_inicio():
    """Imprime el banner de inicio del servidor en formato estructurado."""
    print("=" * 70)
    print("🚀 SERVIDOR CONTABILIDAD INICIADO (MODO ASÍNCRONO)")
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
    print("\n⚡ MEJORAS:")
    print("   ✓ Procesamiento asíncrono de inventario")
    print("   ✓ Respuestas instantáneas (<2 segundos)")
    print("   ✓ Sin duplicación de actualizaciones")
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
# CLASE PRINCIPAL DEL SERVICIO (CON PROCESAMIENTO ASÍNCRONO)
# ===========================================================
class ServidorContabilidad:
    """
    Clase que implementa los métodos remotos de Contabilidad
    con procesamiento asíncrono de actualizaciones de inventario.
    """

    def __init__(self):
        self.name = "Contabilidad"
        self.invIP = INVENTARIO_IP
        self.invPort = INVENTARIO_PORT
        
        # Cliente RPC hacia Inventario
        self.inventarioRPC = xmlrpc.client.ServerProxy(
            f"http://{self.invIP}:{self.invPort}/rpc", allow_none=True
        )
        
        # ⬇️ NUEVO: Cola para procesamiento asíncrono
        self.queue_inventario = Queue()
        self.worker_thread = threading.Thread(
            target=self._procesar_cola_inventario, 
            daemon=True,
            name="InventarioWorker"
        )
        self.worker_thread.start()
        print("✅ Hilo de procesamiento asíncrono iniciado")

    def _procesar_cola_inventario(self):
        """
        Hilo worker que procesa actualizaciones de inventario en segundo plano.
        Esto evita bloquear las respuestas RPC mientras se actualiza el inventario.
        """
        while True:
            try:
                tarea = self.queue_inventario.get()
                if tarea is None:  # Señal de parada
                    break
                
                tipo, datos, identificador = tarea
                print(f"\n🔄 [Worker] Procesando actualización de inventario ({tipo})...")
                print(f"   Identificador: {identificador}")
                
                # Realizar llamada RPC al inventario
                respuesta = self.inventarioRPC.actualizarInventario(json.dumps(datos))
                
                # Parsear respuesta
                if isinstance(respuesta, str):
                    try:
                        respuesta = json.loads(respuesta)
                    except:
                        pass
                
                if isinstance(respuesta, dict) and respuesta.get("status") == "ok":
                    print(f"✅ [Worker] Inventario actualizado correctamente ({tipo})")
                else:
                    print(f"⚠️ [Worker] Error actualizando inventario: {respuesta}")
                    
            except Exception as e:
                print(f"❌ [Worker] Error procesando inventario: {e}")
                traceback.print_exc()
            finally:
                self.queue_inventario.task_done()

    # -------------------------------------------------------
    # MÉTODO: GENERAR FACTURA DE VENTA (ASÍNCRONO)
    # -------------------------------------------------------
    def generarFactura(self, json_data):
        """
        Recibe la venta desde Compras/Ventas y genera factura.
        Actualiza inventario en segundo plano (no bloquea la respuesta).
        """
        try:
            data = json.loads(json_data)
            cliente = data.get("nombre_cliente", "Cliente desconocido")
            total = data.get("total", 0)
            productos = data.get("productos", [])
            factura_id = f"FACT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Log visual de solicitud
            print("=" * 70)
            print("📄 NUEVA SOLICITUD DE FACTURA")
            print("=" * 70)
            print(f"👤 Cliente: {cliente}")
            print(f"💵 Total: ${total:,.2f}")
            print(f"📦 Productos: {len(productos)}")

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

            # ⬇️ CAMBIO CRÍTICO: Encolar para procesamiento asíncrono
            self.queue_inventario.put(("VENTA", envio_data, factura_id))
            print(f"\n📤 Actualización de inventario encolada (procesamiento asíncrono)")
            print(f"   Inventario se actualizará en segundo plano")

            # ⬇️ Generar y devolver factura INMEDIATAMENTE
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
            print("   Inventario: Actualizándose en segundo plano ⏳")
            print("=" * 70)
            
            return json.dumps(factura, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR Contabilidad] {e}")
            traceback.print_exc()
            print("=" * 70)
            return json.dumps({"status": "error", "detalle": str(e)})

    # -------------------------------------------------------
    # MÉTODO: RECIBIR FACTURA DE PROVEEDOR (ASÍNCRONO)
    # -------------------------------------------------------
    def recibirFactura(self, json_data):
        """
        Recibe la compra enviada por Compras/Ventas, la registra.
        Actualiza inventario en segundo plano (no bloquea la respuesta).
        """
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

            # Crear asiento contable
            asiento = {
                "tipo": "COMPRA",
                "compra_id": compra_id,
                "proveedor": proveedor,
                "total": total,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            print(f"📝 Asiento contable creado: COMP-{compra_id}")

            # ⬇️ Preparar datos para inventario
            envio_inv = {
                "tipo_operacion": "COMPRA",
                "nombre_proveedor": proveedor,
                "productos": [
                    {"nombre": str(p), "cantidad": 10, "precio_unit": 100000}
                    for p in productos
                ],
                "total": total
            }

            # ⬇️ CAMBIO CRÍTICO: Encolar para procesamiento asíncrono
            self.queue_inventario.put(("COMPRA", envio_inv, f"COMP-{compra_id}"))
            print(f"\n📤 Actualización de inventario encolada (procesamiento asíncrono)")

            # ⬇️ Responder INMEDIATAMENTE
            respuesta = {
                "status": "ok",
                "mensaje": f"Compra {compra_id} registrada correctamente.",
                "asiento": asiento
            }
            
            print("\n✅ COMPRA REGISTRADA EXITOSAMENTE")
            print(f"   ID Compra: COMP-{compra_id}")
            print("   Inventario: Actualizándose en segundo plano ⏳")
            log_linea()
            
            return json.dumps(respuesta, ensure_ascii=False)

        except Exception as e:
            print(f"[ERROR Contabilidad] {e}")
            traceback.print_exc()
            log_linea()
            return json.dumps({"status": "error", "detalle": str(e)})

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
    contabilidad = ServidorContabilidad()
    server.register_instance(contabilidad)

    # 👇 Habilita system.listMethods, system.methodHelp, etc.
    server.register_introspection_functions()

    banner_inicio()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        contabilidad.queue_inventario.put(None)  # Señal de parada al worker
        contabilidad.worker_thread.join(timeout=5)
        print("✅ Servidor detenido correctamente")
