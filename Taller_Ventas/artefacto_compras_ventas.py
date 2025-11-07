"""
Módulo de Compras y Ventas - Sistema Orquestado de Tienda de Muebles
======================================================================

Este módulo implementa el servicio RPC central para gestionar todas las
operaciones de compras y ventas de la tienda.

Responsabilidades:
    - Registrar ventas solicitadas por el módulo Tienda
    - Registrar compras iniciadas por el módulo AtenciónProveedores
    - Comunicarse con Contabilidad para generación de facturas
    - Mantener historial de transacciones en memoria

Arquitectura:
    - Servidor XML-RPC multihilo (ThreadingMixIn)
    - Comunicación síncrona con timeouts extendidos (90s)
    - Thread-safe mediante locks para estructuras compartidas
    - Respuestas estructuradas en formato dict/JSON

Dependencias:
    - Contabilidad (25.21.199.213:10010) - Generación de facturas
    - Inventario (25.21.199.213:8010) - No se comunica directamente

Autor: Molixx13
Fecha: 2025-11-05
Versión: 2.0 (optimizada con timeouts y sin duplicación de inventario)
"""

from datetime import datetime
import json
import socket
import threading
import traceback
import http.client
from typing import Dict, List, Union, Optional, Any

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import xmlrpc.client

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

# Configuración de red para Contabilidad
IP_CONTABILIDAD: str = "25.21.199.213" # AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀
PUERTO_CONTABILIDAD: int = 10010 # AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀👀
CONTABILIDAD_RPC_URL: str = f"http://{IP_CONTABILIDAD}:{PUERTO_CONTABILIDAD}"

# Puerto de escucha de este servicio
PUERTO_COMPRAS_VENTAS: int = 9000

# URL del servicio de Inventario (no se usa directamente en este módulo)
INVENTARIO_RPC_URL: str = "http://25.21.199.213:8010/rpc"

# Timeout global para conexiones RPC (90 segundos)
socket.setdefaulttimeout(90)

# Lock para operaciones thread-safe
_lock: threading.Lock = threading.Lock()

# ============================================================================
# ALMACENAMIENTO EN MEMORIA
# ============================================================================

ventas: Dict[int, Dict[str, Any]] = {}
"""
Diccionario de ventas registradas.

Estructura:
    {
        venta_id: {
            "id": int,
            "cliente": str,
            "productos": List[str],
            "total": float,
            "fecha": str (formato: YYYY-MM-DD HH:MM:SS)
        }
    }
"""

compras: Dict[int, Dict[str, Any]] = {}
"""
Diccionario de compras registradas.

Estructura:
    {
        compra_id: {
            "id": int,
            "proveedor": str,
            "productos": List[str],
            "total": float,
            "fecha": str (formato: YYYY-MM-DD HH:MM:SS)
        }
    }
"""

facturas: Dict[int, Dict[str, Any]] = {}
"""
Diccionario de facturas recibidas desde Contabilidad.

Estructura:
    {
        venta_id: {
            "factura_id": str,
            "tipo": str,
            "cliente": str,
            "productos": List[Dict],
            "total": float,
            "estado": str,
            "fecha": str
        }
    }
"""

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _next_id(collection: Dict[int, Any]) -> int:
    """
    Genera el siguiente ID disponible para una colección de forma thread-safe.
    
    Args:
        collection (Dict[int, Any]): Diccionario al cual generar ID.
        
    Returns:
        int: Próximo ID disponible (len(collection) + 1).
        
    Note:
        Esta función es thread-safe gracias al uso de _lock.
    """
    with _lock:
        return len(collection) + 1


def obtener_ip_local() -> str:
    """
    Obtiene la dirección IP local de la máquina.
    
    Returns:
        str: Dirección IP local (ej: "192.168.1.100").
        
    Note:
        Utiliza una conexión UDP dummy a 8.8.8.8 para determinar
        la interfaz de red activa.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


class TimeoutTransport(xmlrpc.client.Transport):
    """
    Transporte HTTP personalizado para XML-RPC con timeout configurable.
    
    Attributes:
        timeout (int): Tiempo máximo de espera en segundos.
        
    Example:
        >>> transport = TimeoutTransport(timeout=60)
        >>> proxy = xmlrpc.client.ServerProxy(url, transport=transport)
    """
    
    def __init__(self, timeout: int = 90):
        """
        Inicializa el transporte con un timeout específico.
        
        Args:
            timeout (int, optional): Tiempo de espera en segundos. Default: 90.
        """
        super().__init__()
        self.timeout = timeout
    
    def make_connection(self, host: str) -> http.client.HTTPConnection:
        """
        Crea una conexión HTTP con el timeout configurado.
        
        Args:
            host (str): Host destino.
            
        Returns:
            http.client.HTTPConnection: Conexión HTTP configurada.
        """
        return http.client.HTTPConnection(host, timeout=self.timeout)


def _safe_serverproxy(url: str, timeout: int = 90) -> Optional[xmlrpc.client.ServerProxy]:
    """
    Crea un ServerProxy de XML-RPC con manejo de errores y timeout personalizado.
    
    Args:
        url (str): URL del servicio RPC (ej: "http://localhost:8000/rpc").
        timeout (int, optional): Timeout en segundos. Default: 90.
        
    Returns:
        Optional[xmlrpc.client.ServerProxy]: Proxy configurado o None si hay error.
        
    Example:
        >>> proxy = _safe_serverproxy("http://localhost:8000/rpc", timeout=60)
        >>> if proxy:
        ...     result = proxy.some_method()
    """
    try:
        return xmlrpc.client.ServerProxy(
            url, 
            allow_none=True,
            transport=TimeoutTransport(timeout=timeout)
        )
    except Exception as e:
        print(f"⚠️ Error creando ServerProxy({url}): {e}")
        return None


def _parse_rpc_response(resp: Union[str, Dict, Any]) -> Dict[str, Any]:
    """
    Normaliza respuestas RPC que pueden venir como string JSON o dict.
    
    Args:
        resp (Union[str, Dict, Any]): Respuesta del servidor RPC.
        
    Returns:
        Dict[str, Any]: Respuesta normalizada como diccionario.
        
    Example:
        >>> resp = '{"status": "ok", "value": 123}'
        >>> parsed = _parse_rpc_response(resp)
        >>> print(parsed["status"])  # "ok"
    """
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


def conectar_con_contabilidad() -> Optional[xmlrpc.client.ServerProxy]:
    """
    Establece conexión con el servicio de Contabilidad.
    
    Returns:
        Optional[xmlrpc.client.ServerProxy]: Proxy a Contabilidad o None si falla.
        
    Note:
        Utiliza timeout de 90 segundos para evitar bloqueos.
    """
    return _safe_serverproxy(CONTABILIDAD_RPC_URL, timeout=90)

# ============================================================================
# FUNCIONES RPC EXPUESTAS
# ============================================================================

def registrar_venta(
    cliente: Union[str, Dict[str, Any]], 
    productos: Optional[List[str]] = None, 
    total: Optional[float] = None
) -> Dict[str, Any]:
    """
    Registra una venta realizada desde el módulo Tienda.
    
    Este método acepta múltiples formatos de entrada para facilitar la
    integración con diferentes clientes RPC.
    
    Args:
        cliente (Union[str, Dict]): Nombre del cliente o dict con todos los datos.
            - Si es str con formato JSON: se parsea como dict completo.
            - Si es dict: debe contener keys 'cliente', 'productos', 'total'.
            - Si es str simple: se usa como nombre de cliente.
        productos (Optional[List[str]]): Lista de productos vendidos.
        total (Optional[float]): Monto total de la venta.
        
    Returns:
        Dict[str, Any]: Respuesta estructurada con:
            - status (str): "ok" o "error"
            - mensaje (str): Descripción del resultado
            - id_venta (int): ID asignado a la venta
            - venta (Dict): Objeto de venta completo
            - factura (Optional[Dict]): Factura generada por Contabilidad
            
    Raises:
        No lanza excepciones directamente, todas se capturan y retornan
        en el dict de respuesta con status="error".
        
    Example:
        >>> # Llamada simple
        >>> resultado = registrar_venta("Juan Pérez", ["Mesa"], 100000.0)
        >>> print(resultado["id_venta"])  # 1
        
        >>> # Llamada con JSON
        >>> datos = '{"cliente": "María", "productos": ["Silla"], "total": 50000}'
        >>> resultado = registrar_venta(datos)
        
    Flujo:
        1. Normaliza los datos de entrada
        2. Genera ID único y registra la venta localmente
        3. Solicita factura a Contabilidad (con timeout de 90s)
        4. Almacena la factura recibida
        5. Retorna respuesta estructurada
        
    Note:
        - La venta se registra SIEMPRE, incluso si Contabilidad no responde
        - Contabilidad es responsable de actualizar el inventario
        - Thread-safe mediante uso de _lock
    """
    try:
        # Normalizar input a formato dict estándar
        if isinstance(cliente, str) and cliente.strip().startswith("{"):
            try:
                data = json.loads(cliente)
            except Exception:
                data = {"cliente": cliente}
        elif isinstance(cliente, dict):
            data = cliente
        else:
            data = {"cliente": cliente, "productos": productos, "total": total}

        # Extraer datos con valores por defecto
        cliente_name = data.get("cliente", "Cliente desconocido")
        productos_list = data.get("productos") or ["Sin producto"]
        total_val = float(data.get("total") or 0.0)

        # Generar ID y crear objeto de venta (thread-safe)
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

        # Log visual para monitoreo
        print("\n" + "="*70)
        print("💰 NUEVA VENTA REGISTRADA")
        print("="*70)
        print(f"👤 Cliente: {cliente_name}")
        print(f"🪑 Productos: {', '.join(str(p) for p in productos_list)}")
        print(f"💵 Total: ${total_val:,.2f}")
        print(f"🆔 ID Venta: {venta_id}")
        print("="*70)

        # Solicitar factura a Contabilidad
        factura = None
        cont = conectar_con_contabilidad()
        
        if cont:
            try:
                payload = {
                    "tipo_operacion": "VENTA",
                    "nombre_cliente": cliente_name,
                    "productos": [
                        {
                            "nombre": str(p), 
                            "cantidad": 1, 
                            "precio_unit": (total_val / max(1, len(productos_list)))
                        }
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

        # Retornar respuesta estructurada
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


def registrar_compra(
    proveedor: Optional[Union[str, Dict[str, Any]]] = None,
    productos: Optional[List[str]] = None,
    total: Optional[float] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Registra una compra iniciada por el módulo AtenciónProveedores.
    
    Este método NO actualiza el inventario directamente. Contabilidad es
    el único responsable de actualizar el inventario tras recibir la factura.
    
    Args:
        proveedor (Optional[Union[str, Dict]]): Nombre del proveedor o dict completo.
        productos (Optional[List[str]]): Lista de productos comprados.
        total (Optional[float]): Monto total de la compra.
        data (Optional[Union[str, Dict]]): Datos completos en JSON o dict.
        
    Returns:
        Dict[str, Any]: Respuesta estructurada con:
            - status (str): "ok" o "error"
            - mensaje (str): Descripción del resultado
            - id_compra (int): ID asignado a la compra
            - compra (Dict): Objeto de compra completo
            - respuesta_contabilidad (Dict): Respuesta de Contabilidad
            
    Example:
        >>> resultado = registrar_compra(
        ...     proveedor="MueblesXYZ",
        ...     productos=["Mesa", "Silla"],
        ...     total=500000.0
        ... )
        >>> print(resultado["id_compra"])  # 1
        
    Flujo:
        1. Normaliza los datos de entrada
        2. Genera ID único y registra la compra localmente
        3. Envía factura a Contabilidad (quien actualiza el inventario)
        4. Retorna respuesta con estado de Contabilidad
        
    Important:
        - NO actualiza el inventario directamente
        - Contabilidad es el ÚNICO responsable de actualizar inventario
        - Esto evita duplicaciones y mantiene responsabilidad única
        
    Note:
        - Thread-safe mediante uso de _lock
        - Timeout de 90 segundos para llamadas a Contabilidad
    """
    try:
        # Normalización robusta de entrada
        try:
            if isinstance(proveedor, str):
                try:
                    data = json.loads(proveedor)
                except Exception:
                    data = {
                        "proveedor": proveedor, 
                        "productos": productos or [], 
                        "total": total or 0.0
                    }
            elif isinstance(proveedor, dict):
                data = proveedor
            elif data:
                if isinstance(data, str):
                    data = json.loads(data)
            else:
                data = {
                    "proveedor": proveedor, 
                    "productos": productos or [], 
                    "total": total or 0.0
                }
        except Exception as e:
            print(f"⚠️ Error interpretando datos de compra: {e}")
            data = {
                "proveedor": proveedor, 
                "productos": productos or [], 
                "total": total or 0.0
            }

        # Extraer datos normalizados
        proveedor_name = data.get("proveedor", "Proveedor desconocido")
        productos_list = data.get("productos") or []
        total_val = float(data.get("total") or 0.0)

        # Registrar compra localmente (thread-safe)
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

        # Log visual
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
            respuesta_cont = {
                "status": "pendiente", 
                "detalle": "Contabilidad no disponible"
            }

        # IMPORTANTE: NO actualizar inventario aquí
        print("ℹ️ Inventario será actualizado por Contabilidad (evitando duplicación)")

        # Respuesta final
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


def consultar_ventas() -> Dict[str, Any]:
    """
    Retorna todas las ventas registradas.
    
    Returns:
        Dict[str, Any]: Diccionario con:
            - total (int): Cantidad de ventas registradas
            - data (Dict[int, Dict]): Diccionario completo de ventas
            
    Example:
        >>> resultado = consultar_ventas()
        >>> print(f"Total ventas: {resultado['total']}")
        >>> for venta_id, venta in resultado['data'].items():
        ...     print(f"Venta {venta_id}: {venta['cliente']}")
    """
    with _lock:
        return {"total": len(ventas), "data": ventas}


def consultar_compras() -> Dict[str, Any]:
    """
    Retorna todas las compras registradas.
    
    Returns:
        Dict[str, Any]: Diccionario con:
            - total (int): Cantidad de compras registradas
            - data (Dict[int, Dict]): Diccionario completo de compras
            
    Example:
        >>> resultado = consultar_compras()
        >>> print(f"Total compras: {resultado['total']}")
    """
    with _lock:
        return {"total": len(compras), "data": compras}


def consultar_facturas() -> Dict[str, Any]:
    """
    Retorna todas las facturas recibidas de Contabilidad.
    
    Returns:
        Dict[str, Any]: Diccionario con:
            - total (int): Cantidad de facturas almacenadas
            - data (Dict[int, Dict]): Diccionario completo de facturas
            
    Example:
        >>> resultado = consultar_facturas()
        >>> print(f"Total facturas: {resultado['total']}")
    """
    with _lock:
        return {"total": len(facturas), "data": facturas}

# ============================================================================
# SERVIDOR XML-RPC
# ============================================================================

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """
    Servidor XML-RPC con soporte multihilo.
    
    Permite manejar múltiples peticiones concurrentes sin bloqueos.
    Hereda de ThreadingMixIn para crear un thread por cada conexión.
    """
    pass


class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Manejador de peticiones HTTP para el servidor XML-RPC.
    
    Attributes:
        rpc_paths (tuple): Rutas aceptadas para peticiones RPC.
    """
    rpc_paths = ("/rpc",)


def iniciar_servidor() -> None:
    """
    Inicia el servidor XML-RPC de Compras/Ventas.
    
    Configura y arranca el servidor multihilo que escucha en todas las
    interfaces de red (0.0.0.0) en el puerto configurado.
    
    Métodos RPC expuestos:
        - registrar_venta(cliente, productos, total)
        - registrar_compra(proveedor, productos, total, data)
        - obtener_ip_local()
        - consultar_ventas()
        - consultar_compras()
        - consultar_facturas()
        
    Raises:
        KeyboardInterrupt: Capturado para detención limpia del servidor.
        Exception: Cualquier error fatal se registra y propaga.
        
    Note:
        El servidor corre indefinidamente hasta recibir KeyboardInterrupt (Ctrl+C).
    """
    ip = obtener_ip_local()
    puerto = PUERTO_COMPRAS_VENTAS
    host_escucha = "0.0.0.0"

    # Banner de inicio
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

    # Crear e inicializar servidor
    server = ThreadedXMLRPCServer(
        (host_escucha, puerto), 
        requestHandler=RequestHandler, 
        allow_none=True
    )
    
    # Registrar métodos RPC
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

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    iniciar_servidor()
