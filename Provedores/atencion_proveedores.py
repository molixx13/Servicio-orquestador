#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Atención a Proveedores - Sistema Orquestado de Tienda de Muebles
============================================================================

Este módulo gestiona las relaciones con proveedores externos y procesa
requerimientos de reabastecimiento desde el módulo de Inventario.

Responsabilidades:
    - Recibir requerimientos de productos con bajo stock
    - Simular gestión de compras con proveedores externos
    - Notificar compras al módulo Compras/Ventas
    - Mantener historial local de compras realizadas
    - NO actualiza inventario directamente (delegado a Contabilidad)

Arquitectura:
    - Servidor XML-RPC escuchando en /rpc
    - Comunicación unidireccional: Inventario → Proveedores → Compras/Ventas
    - Almacenamiento persistente en compras_proveedores.json
    - Sin duplicación de actualizaciones de inventario

Flujo típico:
    1. Inventario detecta stock bajo
    2. Inventario llama a procesarRequerimiento()
    3. AtenciónProveedores registra compra local
    4. AtenciónProveedores notifica a Compras/Ventas
    5. Compras/Ventas notifica a Contabilidad
    6. Contabilidad actualiza inventario (responsabilidad única)

Mejoras vs versión anterior:
    - ✅ NO actualiza inventario (evita duplicación)
    - ✅ Responsabilidad única clara
    - ✅ Sin llamadas redundantes

Dependencias:
    - Compras/Ventas (192.168.100.233:9000) - Registro de compras
    - Inventario (indirectamente vía Compras/Ventas)

Autor: Molixx13
Fecha: 2025-11-05
Versión: 2.0 (sin duplicación de inventario)
"""

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import xmlrpc.client
import json
import os
import socket
from datetime import datetime
from typing import Dict, List, Any, Union

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

hostIP: str = str(socket.gethostbyname(socket.gethostname()))
"""Dirección IP local de esta máquina."""

port: int = 7005
"""Puerto de escucha del servidor de AtenciónProveedores."""

# URLs de servicios externos
COMPRAS_VENTAS_RPC_URL: str = "http://192.168.100.233:9000/rpc"
"""URL del módulo Compras/Ventas."""

CONTABILIDAD_RPC_URL: str = "http://25.21.199.213:10010"
"""URL del módulo Contabilidad (referencia, no se usa directamente)."""

# Archivo de persistencia local
DATA_FILE: str = "compras_proveedores.json"
"""Archivo JSON para almacenar historial de compras."""

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_compras() -> List[Dict[str, Any]]:
    """
    Carga el historial de compras desde el archivo JSON.
    
    Si el archivo no existe, lo crea con una lista vacía.
    Si el archivo está corrupto, retorna lista vacía.
    
    Returns:
        List[Dict[str, Any]]: Lista de compras registradas.
        
    Example:
        >>> compras = cargar_compras()
        >>> for compra in compras:
        ...     print(compra["id"], compra["proveedor"])
        
    Note:
        El archivo se crea automáticamente en el primer uso.
    """
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return []
        
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def guardar_compras(compras: List[Dict[str, Any]]) -> None:
    """
    Guarda el historial de compras en el archivo JSON.
    
    Args:
        compras (List[Dict[str, Any]]): Lista completa de compras a guardar.
        
    Example:
        >>> compras = cargar_compras()
        >>> compras.append({"id": "COMP-001", "proveedor": "ABC"})
        >>> guardar_compras(compras)
        
    Note:
        Sobrescribe completamente el archivo con la lista proporcionada.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(compras, f, indent=4, ensure_ascii=False)


def _parse_rpc_response(resp: Union[str, Dict, Any]) -> Dict[str, Any]:
    """
    Normaliza respuestas RPC que pueden venir como string JSON o dict.
    
    Args:
        resp (Union[str, Dict, Any]): Respuesta del servidor RPC.
        
    Returns:
        Dict[str, Any]: Respuesta normalizada como diccionario.
        
    Example:
        >>> resp = '{"status": "ok"}'
        >>> parsed = _parse_rpc_response(resp)
        >>> print(parsed["status"])  # "ok"
        
    Note:
        Si el parsing falla, retorna dict con keys "error_parse" y "raw".
    """
    try:
        if isinstance(resp, str):
            return json.loads(resp)
        return resp
    except Exception as e:
        return {"error_parse": str(e), "raw": resp}


def banner_inicio() -> None:
    """
    Imprime el banner informativo del servidor al iniciar.
    
    Muestra:
        - Configuración de red
        - Métodos RPC disponibles
        - Mejoras implementadas
        - Recordatorio sobre responsabilidad única
    """
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
    print("\n⏳ Esperando llamadas RPC...\n")

# ============================================================================
# CLASE PRINCIPAL DEL SERVICIO
# ============================================================================

class ServidorAtencionProveedores:
    """
    Servicio de gestión de proveedores y procesamiento de requerimientos.
    
    Esta clase maneja la comunicación con proveedores externos simulados
    y coordina con el módulo Compras/Ventas para registrar las compras.
    
    Attributes:
        compras_rpc (ServerProxy): Cliente RPC hacia Compras/Ventas.
        
    Important:
        Este servicio NO actualiza el inventario directamente.
        Toda actualización de inventario es responsabilidad de Contabilidad.
        
    Example:
        >>> servidor = ServidorAtencionProveedores()
        >>> # El servidor queda listo para recibir llamadas RPC
    """
    
    def __init__(self):
        """
        Inicializa el servidor y establece conexión con Compras/Ventas.
        """
        self.compras_rpc = xmlrpc.client.ServerProxy(
            COMPRAS_VENTAS_RPC_URL, 
            allow_none=True
        )

    def procesarRequerimiento(self, json_data: str) -> Dict[str, Any]:
        """
        Procesa un requerimiento de productos desde el módulo Inventario.
        
        Este método es invocado automáticamente cuando el Inventario detecta
        productos con stock bajo. Simula la compra a proveedores y notifica
        a Compras/Ventas para su registro contable.
        
        Args:
            json_data (str): Requerimiento en formato JSON con estructura:
                {
                    "origen": "Inventario",
                    "productos": [
                        {
                            "nombre": str,
                            "cantidad": int
                        }
                    ],
                    "motivo": str,
                    "proveedor": str (opcional, default "ProveedorXYZ")
                }
                
        Returns:
            Dict[str, Any]: Respuesta estructurada con:
                - status (str): "ok" o "error"
                - mensaje (str): Descripción del resultado
                - compra_id (str): ID único de la compra (COMP-TIMESTAMP)
                - respuesta_compras (Dict): Respuesta de Compras/Ventas
                
        Example:
            >>> datos = {
            ...     "origen": "Inventario",
            ...     "productos": [
            ...         {"nombre": "Mesa", "cantidad": 10},
            ...         {"nombre": "Silla", "cantidad": 20}
            ...     ],
            ...     "motivo": "Reabastecimiento automático"
            ... }
            >>> resultado = servidor.procesarRequerimiento(json.dumps(datos))
            >>> print(resultado["compra_id"])  # COMP-20251105143000
            
        Flujo detallado:
            1. **Parsear datos** de entrada
            2. **Validar** que haya productos en el requerimiento
            3. **Registrar compra local** en archivo JSON
            4. **Calcular total** (cantidad * 100,000 por producto)
            5. **Conectar con Compras/Ventas**:
                - Probar conexión (consultar_compras)
                - Enviar orden de compra (registrar_compra)
            6. **Verificar respuesta** de Contabilidad
            7. **NO actualizar inventario** (lo hace Contabilidad)
            8. **Retornar resultado**
            
        Important:
            - Este método NO actualiza el inventario directamente
            - Confía en que Contabilidad actualizará el inventario
            - Evita duplicación de actualizaciones
            
        Note:
            - El ID de compra usa timestamp: COMP-YYYYMMDDHHMMSS
            - El total se calcula como: sum(cantidad * 100000)
            - Proveedor por defecto: "ProveedorXYZ"
            
        Raises:
            No lanza excepciones. Errores retornan dict con status="error".
        """
        try:
            data = json.loads(json_data)
            productos = data.get("productos", [])
            proveedor = data.get("proveedor", "ProveedorXYZ")

            # Log del requerimiento recibido
            print("=" * 70)
            print("📦 REQUERIMIENTO RECIBIDO DESDE INVENTARIO")
            print("=" * 70)
            print(json.dumps(data, indent=4, ensure_ascii=False))
            print("=" * 70)

            # Validación básica
            if not productos:
                return {
                    "status": "error", 
                    "mensaje": "Sin productos en el requerimiento"
                }

            # Registrar compra localmente
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

            # Log de productos
            print("🪑 Productos solicitados:")
            for p in productos:
                print(f"   • {p['nombre']} x{p['cantidad']}")

            # Calcular total (valor simulado: $100,000 por unidad)
            total = sum(p["cantidad"] * 100000 for p in productos)

            # ================================================================
            # ENVIAR ORDEN DE COMPRA A COMPRAS/VENTAS
            # ================================================================
            print(f"\n📡 Enviando orden de compra a Compras/Ventas ({COMPRAS_VENTAS_RPC_URL}) ...")
            
            try:
                # Crear cliente RPC
                compras_rpc = xmlrpc.client.ServerProxy(
                    COMPRAS_VENTAS_RPC_URL, 
                    allow_none=True
                )

                # Probar conexión consultando compras existentes
                ping_raw = compras_rpc.consultar_compras()
                ping = _parse_rpc_response(ping_raw)
                
                total_compras = (
                    ping.get("total", 0)
                    if isinstance(ping, dict)
                    else len(ping) if isinstance(ping, list)
                    else 0
                )
                
                print(f"✅ Conexión confirmada. Compras registradas actualmente: {total_compras}")

                # Preparar payload para Compras/Ventas
                payload = {
                    "proveedor": proveedor,
                    "productos": [p["nombre"] for p in productos],  # Solo nombres
                    "total": total
                }
                
                # Enviar orden de compra
                respuesta_raw = compras_rpc.registrar_compra(json.dumps(payload))
                respuesta = _parse_rpc_response(respuesta_raw)

                print("✅ Orden de compra enviada a Compras/Ventas.")
                print(f"📥 Respuesta recibida:\n{json.dumps(respuesta, indent=4, ensure_ascii=False)}")

                # Verificar si Contabilidad procesó correctamente
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

            # ================================================================
            # IMPORTANTE: NO ACTUALIZAR INVENTARIO AQUÍ
            # ================================================================
            print("\nℹ️ Inventario actualizado por Contabilidad (responsabilidad única)")
            print("   └─ NO se realiza actualización duplicada desde este módulo")

            # Respuesta final
            return {
                "status": "ok",
                "mensaje": "Requerimiento procesado correctamente",
                "compra_id": compra_id,
                "respuesta_compras": respuesta
            }

        except Exception as e:
            print(f"❌ Error en procesarRequerimiento: {e}")
            return {"status": "error", "detalle": str(e)}

    def listarCompras(self) -> Dict[str, Any]:
        """
        Retorna todas las compras registradas a proveedores.
        
        Returns:
            Dict[str, Any]: Diccionario con:
                - total (int): Cantidad de compras registradas
                - data (List[Dict]): Lista completa de compras
                
        Example:
            >>> resultado = servidor.listarCompras()
            >>> print(f"Total: {resultado['total']}")
            >>> for compra in resultado['data']:
            ...     print(f"{compra['id']}: {compra['proveedor']}")
                
        Note:
            Lee el archivo compras_proveedores.json en cada llamada
            para obtener datos actualizados.
        """
        compras = cargar_compras()
        return {"total": len(compras), "data": compras}

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# ============================================================================

class RequestHandler(SimpleXMLRPCRequestHandler):
    """
    Manejador de peticiones HTTP para el servidor XML-RPC.
    
    Attributes:
        rpc_paths (tuple): Rutas aceptadas para peticiones RPC.
        
    Important:
        Solo acepta peticiones en /rpc (no /RPC2 ni otras rutas).
        Esto evita errores 404 Not Found.
    """
    rpc_paths = ('/rpc',)

# ============================================================================
# SERVIDOR PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    """
    Punto de entrada del servidor de AtenciónProveedores.
    
    Inicializa:
        - Servidor XML-RPC escuchando en todas las interfaces
        - Instancia de ServidorAtencionProveedores
        - RequestHandler con ruta /rpc
        
    El servidor corre indefinidamente hasta recibir KeyboardInterrupt.
    
    Example:
        $ python atencion_proveedores.py
        🏢 SERVIDOR ATENCIÓN A PROVEEDORES INICIADO
        ...
        ⏳ Esperando llamadas RPC...
    """
    server = SimpleXMLRPCServer(
        (hostIP, port),
        requestHandler=RequestHandler,
        allow_none=True,
        logRequests=True
    )
    
    server.register_instance(ServidorAtencionProveedores())
    banner_inicio()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")