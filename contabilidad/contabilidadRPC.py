#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Contabilidad - Sistema Orquestado de Tienda de Muebles
==================================================================

Este módulo implementa el servicio de contabilidad con procesamiento asíncrono
para gestionar facturas de ventas y compras, y actualizar el inventario.

Responsabilidades:
    - Generar facturas oficiales para todas las ventas
    - Registrar y contabilizar compras a proveedores
    - Actualizar el inventario tras cada transacción (RESPONSABILIDAD ÚNICA)
    - Mantener numeración consecutiva de facturas
    - Crear asientos contables

Arquitectura:
    - Servidor XML-RPC con procesamiento asíncrono
    - Thread worker para actualizar inventario en segundo plano
    - Cola (Queue) para encolar actualizaciones de inventario
    - Respuestas inmediatas (<2 segundos) sin bloqueos

Mejoras vs versión anterior:
    - ✅ Procesamiento asíncrono elimina timeouts
    - ✅ Respuestas instantáneas al cliente
    - ✅ Inventario se actualiza en segundo plano
    - ✅ Sin duplicación de actualizaciones

Dependencias:
    - Inventario (25.21.199.213:8010) - Actualización de stock

Autor: Molixx13
Fecha: 2025-11-05
Versión: 2.0 (con procesamiento asíncrono)
"""

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import json
import socket
from datetime import datetime
import threading
from queue import Queue
import traceback
from typing import Dict, Any, Tuple, Optional

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

hostIP: str = str(socket.gethostbyname(socket.gethostname()))
"""Dirección IP local de esta máquina."""

port: int = 10010
"""Puerto de escucha del servidor de Contabilidad."""

# Configuración del servicio de Inventario
INVENTARIO_IP: str = "25.21.199.213"
INVENTARIO_PORT: int = 8010

# ============================================================================
# CLASES AUXILIARES
# ============================================================================

class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Manejador de peticiones HTTP para el servidor XML-RPC.
    
    Attributes:
        rpc_paths (tuple): Rutas aceptadas (/rpc y /RPC2 para compatibilidad).
    """
    rpc_paths = ('/rpc', '/RPC2')

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def banner_inicio() -> None:
    """
    Imprime el banner informativo del servidor al iniciar.
    
    Muestra configuración de red, métodos disponibles y mejoras implementadas.
    """
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


def log_linea() -> None:
    """Imprime una línea separadora uniforme para logs."""
    print("=" * 70)


def log_evento(mensaje: str) -> None:
    """
    Registra un evento con timestamp.
    
    Args:
        mensaje (str): Mensaje a registrar.
        
    Example:
        >>> log_evento("Factura generada")
        [2025-11-05 14:30:00] Factura generada
    """
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{hora}] {mensaje}")

# ============================================================================
# CLASE PRINCIPAL DEL SERVICIO
# ============================================================================

class ServidorContabilidad:
    """
    Servicio de Contabilidad con procesamiento asíncrono de inventario.
    
    Esta clase implementa los métodos RPC para generar facturas de ventas
    y registrar compras. Utiliza un hilo worker para actualizar el inventario
    en segundo plano, permitiendo respuestas instantáneas al cliente.
    
    Attributes:
        name (str): Nombre del servicio.
        invIP (str): IP del servicio de Inventario.
        invPort (int): Puerto del servicio de Inventario.
        inventarioRPC (ServerProxy): Cliente RPC hacia Inventario.
        queue_inventario (Queue): Cola para actualizaciones asíncronas.
        worker_thread (Thread): Hilo que procesa la cola de inventario.
        
    Example:
        >>> servidor = ServidorContabilidad()
        >>> # El servidor automáticamente inicia el worker thread
        
    Note:
        El worker thread se ejecuta como daemon, por lo que se detendrá
        automáticamente cuando el programa principal termine.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de Contabilidad y su worker thread.
        
        Crea:
            - Conexión RPC hacia Inventario
            - Cola para procesamiento asíncrono
            - Hilo worker en modo daemon
        """
        self.name = "Contabilidad"
        self.invIP = INVENTARIO_IP
        self.invPort = INVENTARIO_PORT
        
        # Cliente RPC hacia Inventario
        self.inventarioRPC = xmlrpc.client.ServerProxy(
            f"http://{self.invIP}:{self.invPort}/rpc", 
            allow_none=True
        )
        
        # Cola para procesamiento asíncrono
        self.queue_inventario: Queue[Optional[Tuple[str, Dict, str]]] = Queue()
        
        # Iniciar worker thread
        self.worker_thread = threading.Thread(
            target=self._procesar_cola_inventario, 
            daemon=True,
            name="InventarioWorker"
        )
        self.worker_thread.start()
        print("✅ Hilo de procesamiento asíncrono iniciado")

    def _procesar_cola_inventario(self) -> None:
        """
        Worker thread que procesa actualizaciones de inventario en segundo plano.
        
        Este método corre en un loop infinito, esperando tareas en la cola.
        Cada tarea contiene los datos necesarios para actualizar el inventario.
        
        Flujo:
            1. Espera tareas en queue_inventario (bloqueante)
            2. Extrae tipo, datos e identificador
            3. Llama a inventarioRPC.actualizarInventario()
            4. Registra el resultado (éxito o error)
            5. Marca la tarea como completada
            
        Note:
            - Se detiene al recibir None en la cola
            - Captura todas las excepciones para evitar que el thread muera
            - Los errores se registran pero no detienen el procesamiento
            
        Example:
            >>> # Este método se ejecuta automáticamente
            >>> # Las tareas se encolan así:
            >>> self.queue_inventario.put(("VENTA", datos, "FACT-123"))
        """
        while True:
            try:
                tarea = self.queue_inventario.get()
                
                # Señal de parada
                if tarea is None:
                    break
                
                tipo, datos, identificador = tarea
                
                print(f"\n🔄 [Worker] Procesando actualización de inventario ({tipo})...")
                print(f"   Identificador: {identificador}")
                
                # Realizar llamada RPC al inventario
                respuesta = self.inventarioRPC.actualizarInventario(json.dumps(datos))
                
                # Parsear respuesta (puede venir como string o dict)
                if isinstance(respuesta, str):
                    try:
                        respuesta = json.loads(respuesta)
                    except:
                        pass
                
                # Verificar resultado
                if isinstance(respuesta, dict) and respuesta.get("status") == "ok":
                    print(f"✅ [Worker] Inventario actualizado correctamente ({tipo})")
                else:
                    print(f"⚠️ [Worker] Error actualizando inventario: {respuesta}")
                    
            except Exception as e:
                print(f"❌ [Worker] Error procesando inventario: {e}")
                traceback.print_exc()
            finally:
                self.queue_inventario.task_done()

    def generarFactura(self, json_data: str) -> str:
        """
        Genera una factura oficial para una venta y actualiza inventario asíncronamente.
        
        Este método es invocado por el módulo Compras/Ventas cuando se registra
        una venta. La actualización del inventario se realiza en segundo plano
        para proporcionar una respuesta inmediata.
        
        Args:
            json_data (str): Datos de la venta en formato JSON con estructura:
                {
                    "tipo_operacion": "VENTA",
                    "nombre_cliente": str,
                    "productos": [
                        {
                            "nombre": str,
                            "cantidad": int,
                            "precio_unit": float
                        }
                    ],
                    "total": float
                }
                
        Returns:
            str: Factura en formato JSON string con estructura:
                {
                    "factura_id": str,
                    "tipo": "venta",
                    "cliente": str,
                    "productos": List[Dict],
                    "total": float,
                    "estado": "Aprobada",
                    "fecha": str
                }
                
        Raises:
            No lanza excepciones. Errores retornan JSON con status="error".
            
        Example:
            >>> datos = {
            ...     "tipo_operacion": "VENTA",
            ...     "nombre_cliente": "Juan Pérez",
            ...     "productos": [{"nombre": "Mesa", "cantidad": 1, "precio_unit": 100000}],
            ...     "total": 100000
            ... }
            >>> factura_json = servidor.generarFactura(json.dumps(datos))
            >>> factura = json.loads(factura_json)
            >>> print(factura["factura_id"])  # FACT-20251105143000
            
        Flujo:
            1. Parsea datos de entrada
            2. Genera ID único de factura (timestamp)
            3. Normaliza productos para envío a Inventario
            4. **Encola** actualización de inventario (NO espera)
            5. Genera y retorna factura INMEDIATAMENTE
            6. Worker thread actualiza inventario en paralelo
            
        Important:
            - La respuesta es inmediata (<1 segundo)
            - El inventario se actualiza en segundo plano
            - La factura se genera SIEMPRE, incluso si Inventario falla
            
        Note:
            Formato de ID: FACT-YYYYMMDDHHMMSS (ej: FACT-20251105143000)
        """
        try:
            data = json.loads(json_data)
            cliente = data.get("nombre_cliente", "Cliente desconocido")
            total = data.get("total", 0)
            productos = data.get("productos", [])
            factura_id = f"FACT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Log visual
            print("=" * 70)
            print("📄 NUEVA SOLICITUD DE FACTURA")
            print("=" * 70)
            print(f"👤 Cliente: {cliente}")
            print(f"💵 Total: ${total:,.2f}")
            print(f"📦 Productos: {len(productos)}")

            # Normalizar productos para Inventario
            envio_data = {
                "tipo_operacion": "VENTA",
                "nombre_cliente": cliente,
                "total": total,
                "productos": []
            }

            productos_raw = data.get("productos", [])
            for p in productos_raw:
                if isinstance(p, dict):
                    # Extraer nombre de diferentes posibles keys
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
                    # Parsear string tipo "Mesa x2"
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

            # CLAVE: Encolar actualización para procesamiento asíncrono
            self.queue_inventario.put(("VENTA", envio_data, factura_id))
            print(f"\n📤 Actualización de inventario encolada (procesamiento asíncrono)")
            print(f"   Inventario se actualizará en segundo plano")

            # Generar factura INMEDIATAMENTE (sin esperar inventario)
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

    def recibirFactura(self, json_data: str) -> str:
        """
        Registra una factura de compra a proveedor y actualiza inventario asíncronamente.
        
        Este método es invocado por el módulo Compras/Ventas cuando se registra
        una compra a un proveedor. Crea el asiento contable y actualiza el
        inventario en segundo plano.
        
        Args:
            json_data (str): Datos de la compra en formato JSON con estructura:
                {
                    "tipo": "COMPRA",
                    "proveedor": str,
                    "productos": List[str],  # Lista de nombres
                    "total": float,
                    "compra_id": int,
                    "fecha": str
                }
                
        Returns:
            str: Respuesta en formato JSON string con estructura:
                {
                    "status": "ok",
                    "mensaje": str,
                    "asiento": {
                        "tipo": "COMPRA",
                        "compra_id": int,
                        "proveedor": str,
                        "total": float,
                        "fecha": str
                    }
                }
                
        Example:
            >>> datos = {
            ...     "tipo": "COMPRA",
            ...     "proveedor": "MueblesXYZ",
            ...     "productos": ["Mesa", "Silla"],
            ...     "total": 500000,
            ...     "compra_id": 1,
            ...     "fecha": "2025-11-05 14:30:00"
            ... }
            >>> respuesta_json = servidor.recibirFactura(json.dumps(datos))
            >>> respuesta = json.loads(respuesta_json)
            >>> print(respuesta["status"])  # "ok"
            
        Flujo:
            1. Parsea datos de la compra
            2. Crea asiento contable
            3. Normaliza productos para Inventario
            4. **Encola** actualización de inventario
            5. Retorna confirmación INMEDIATAMENTE
            6. Worker actualiza inventario en paralelo
            
        Important:
            - Este es el ÚNICO método que debe invocar actualizaciones de
              inventario para compras (responsabilidad única)
            - Respuesta inmediata (<1 segundo)
            - Asiento contable se crea siempre
            
        Note:
            - Cada producto se normaliza con cantidad=10 y precio=100000
            - Estos valores son configurables según necesidad del negocio
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

            # Preparar datos para inventario
            envio_inv = {
                "tipo_operacion": "COMPRA",
                "nombre_proveedor": proveedor,
                "productos": [
                    {
                        "nombre": str(p), 
                        "cantidad": 10,      # Cantidad por defecto
                        "precio_unit": 100000  # Precio por defecto
                    }
                    for p in productos
                ],
                "total": total
            }

            # CLAVE: Encolar actualización asíncrona
            self.queue_inventario.put(("COMPRA", envio_inv, f"COMP-{compra_id}"))
            print(f"\n📤 Actualización de inventario encolada (procesamiento asíncrono)")

            # Responder INMEDIATAMENTE
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

# ============================================================================
# SERVIDOR PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    """
    Punto de entrada del servidor de Contabilidad.
    
    Inicializa:
        - Servidor XML-RPC en todas las interfaces
        - Instancia de ServidorContabilidad (con worker thread)
        - Funciones de introspección (listMethods, methodHelp)
        
    El servidor corre indefinidamente hasta recibir KeyboardInterrupt.
    """
    server = SimpleXMLRPCServer(
        (hostIP, port),
        requestHandler=RequestHandler,
        allow_none=True,
        logRequests=True
    )
    
    contabilidad = ServidorContabilidad()
    server.register_instance(contabilidad)

    # Habilitar introspección RPC
    server.register_introspection_functions()

    banner_inicio()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        # Señal de parada al worker
        contabilidad.queue_inventario.put(None)
        contabilidad.worker_thread.join(timeout=5)
        print("✅ Servidor detenido correctamente")