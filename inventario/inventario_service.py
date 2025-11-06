"""
Servicio de Inventario - Persistente (RPC)
Autor: Molixx13
Descripción:
------------
Servicio XML-RPC para la gestión del inventario de la Tienda de Muebles.
Guarda los datos en disco en el mismo directorio del módulo (inventario_data.json).
"""

import json
import os

import xmlrpc.client
from xmlrpc.client import Transport

ATENCION_PROVEEDORES_RPC_URL = "http://25.21.199.213:7005"


# Archivo de persistencia situado en la misma carpeta que este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTARIO_FILE = os.path.join(BASE_DIR, "inventario_data.json")


class InventarioService:
    def __init__(self):
        """Inicializa el inventario y carga datos persistentes si existen."""
        self.productos = {}
        self.requerimientos = {}
        self.next_product_id = 1
        self.next_requerimiento_id = 1

        self.cargar_datos()  # Intentar restaurar desde disco

    # ===========================================================
    # Persistencia en disco (ruta absoluta)
    # ===========================================================
    def guardar_datos(self):
        """Guarda productos y requerimientos en un archivo JSON (ruta absoluta)."""
        try:
            data = {
                "productos": self.productos,
                "requerimientos": self.requerimientos,
                "next_product_id": self.next_product_id,
                "next_requerimiento_id": self.next_requerimiento_id
            }
            with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"💾 Inventario guardado en disco: {INVENTARIO_FILE}")
        except Exception as e:
            print(f"⚠️ Error guardando inventario: {e}")

    def cargar_datos(self):
        """Carga productos y requerimientos desde un archivo JSON si existe (ruta absoluta)."""
        if os.path.exists(INVENTARIO_FILE):
            try:
                with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # JSON keys are strings; ensure dict keys are ints for product IDs
                productos_raw = data.get("productos", {})
                # If productos saved as dict with string keys, convert keys to int
                productos = {}
                for k, v in productos_raw.items():
                    try:
                        pid = int(k)
                    except Exception:
                        pid = v.get("id", None) or int(k) if str(k).isdigit() else None
                    if pid is None:
                        continue
                    productos[pid] = v
                self.productos = productos

                self.requerimientos = data.get("requerimientos", {})
                self.next_product_id = data.get("next_product_id", 1)
                self.next_requerimiento_id = data.get("next_requerimiento_id", 1)
                print(f"📂 Inventario restaurado desde {INVENTARIO_FILE}")
            except Exception as e:
                print(f"⚠️ Error cargando inventario: {e}")
        else:
            print(f"📄 No se encontró {INVENTARIO_FILE}. Iniciando inventario vacío.")

    # ===========================================================
    # Conectores RPC
    # ===========================================================
    def cargarProductos(self, nombre, descripcion, categoria, precio, stock, stock_minimo=5):
        """CONECTOR 1 - API Tienda: Cargar nuevos productos al inventario"""
        try:
            nuevo_producto = {
                "id": self.next_product_id,
                "nombre": str(nombre),
                "descripcion": str(descripcion),
                "categoria": str(categoria),
                "precio": float(precio),
                "stock": int(stock),
                "stock_minimo": int(stock_minimo)
            }

            self.productos[self.next_product_id] = nuevo_producto
            self.next_product_id += 1
            self.guardar_datos()  # Guarda inmediatamente
            print(f"[Inventario] Producto agregado: {nuevo_producto['nombre']} (ID {nuevo_producto['id']})")

            return {
                "success": True,
                "message": "Producto cargado exitosamente",
                "producto_id": nuevo_producto["id"],
                "data": nuevo_producto
            }

        except Exception as e:
            return {"success": False, "message": f"Error en cargarProductos: {str(e)}"}

    def actualizarInventario(self, producto_id=None, stock=None, precio=None, data=None):
        """Actualiza el inventario tras operaciones desde Contabilidad, Tienda o Compras."""
        try:
            # Normalización de entrada
            if isinstance(producto_id, str):
                try:
                    data = json.loads(producto_id)
                except Exception:
                    data = {"producto_id": producto_id, "stock": stock, "precio": precio}
            elif isinstance(producto_id, dict):
                data = producto_id
            elif isinstance(data, str):
                data = json.loads(data)
            elif data is None:
                data = {"producto_id": producto_id, "stock": stock, "precio": precio}

            print("=" * 70)
            print("📦 SOLICITUD DE ACTUALIZACIÓN DE INVENTARIO")
            print("=" * 70)
            print(json.dumps(data, indent=4, ensure_ascii=False))

            tipo = data.get("tipo_operacion", "").upper()

            # 🔹 Caso: actualización directa
            if "producto_id" in data and tipo not in ["VENTA", "COMPRA"]:
                producto_id = int(data["producto_id"])
                if producto_id not in self.productos:
                    return {"status": "error", "detalle": f"Producto {producto_id} no encontrado"}
                producto = self.productos[producto_id]
                if data.get("stock") is not None:
                    producto["stock"] = int(data["stock"])
                if data.get("precio") is not None:
                    producto["precio"] = float(data["precio"])
                self.guardar_datos()
                print(f"[Inventario] ✅ Producto {producto['nombre']} actualizado directamente.")
                return {"status": "ok", "message": "Inventario actualizado correctamente"}

            # 🔹 Caso: operación tipo VENTA o COMPRA
            elif tipo in ["VENTA", "COMPRA"]:
                productos = data.get("productos", [])
                for p in productos:
                    nombre = p.get("nombre", "").strip()
                    cantidad = int(p.get("cantidad", 1))
                    precio_unit = float(p.get("precio_unit", 0))

                    if " x" in nombre:
                        nombre = nombre.split(" x")[0].strip()

                    encontrado = None
                    for pid, prod in self.productos.items():
                        if prod["nombre"].strip().lower() == nombre.lower():
                            encontrado = pid
                            break

                    if not encontrado:
                        print(f"⚠️ Producto '{nombre}' no encontrado en inventario.")
                        continue

                    producto = self.productos[encontrado]

                    if tipo == "VENTA":
                        nuevo_stock = max(0, producto["stock"] - cantidad)
                        print(f"🛒 Venta: '{nombre}' - stock {producto['stock']} → {nuevo_stock}")
                        producto["stock"] = nuevo_stock

                        # 🚨 Si se detecta bajo stock, generar requerimiento
                        if nuevo_stock <= producto["stock_minimo"]:
                            print(f"⚠️ Stock bajo detectado para '{nombre}' → disparando requerimiento automático.")
                            self.cargarRequerimientosProductos()

                    elif tipo == "COMPRA":
                        nuevo_stock = producto["stock"] + cantidad
                        print(f"📦 Compra: '{nombre}' - stock {producto['stock']} → {nuevo_stock}")
                        producto["stock"] = nuevo_stock
                        if precio_unit > 0:
                            producto["precio"] = precio_unit

                self.guardar_datos()
                print("✅ Inventario actualizado correctamente tras operación contable.")
                return {"status": "ok", "message": f"Inventario actualizado ({tipo})"}

            else:
                return {"status": "error", "detalle": "Tipo de operación no reconocido o datos incompletos"}

        except Exception as e:
            print(f"[Inventario ERROR] {e}")
            return {"status": "error", "detalle": str(e)}

    # Métodos consultivos
    # ===========================================================
    def listarProductos(self):
        """Listar todos los productos del inventario"""
        try:
            productos_lista = list(self.productos.values())
            return {
                "success": True,
                "total_productos": len(productos_lista),
                "data": productos_lista
            }
        except Exception as e:
            return {"success": False, "message": f"Error listando productos: {str(e)}"}

    def obtenerProducto(self, producto_id):
        """Obtener la información de un producto por su ID"""
        try:
            producto_id = int(producto_id)
            if producto_id not in self.productos:
                return {"success": False, "message": f"Producto con ID {producto_id} no encontrado."}
            return {"success": True, "data": self.productos[producto_id]}
        except Exception as e:
            return {"success": False, "message": f"Error obteniendo producto: {str(e)}"}

    def listarRequerimientos(self):
        """Listar requerimientos actuales"""
        try:
            reqs = list(self.requerimientos.values())
            return {
                "success": True,
                "total_requerimientos": len(reqs),
                "data": reqs
            }
        except Exception as e:
            return {"success": False, "message": f"Error listando requerimientos: {str(e)}"}

    def estadisticasInventario(self):
        """Obtener estadísticas del inventario"""
        try:
            total_productos = len(self.productos)
            total_stock = sum(p["stock"] for p in self.productos.values())
            valor_total = sum(p["precio"] * p["stock"] for p in self.productos.values())
            bajo_stock = sum(1 for p in self.productos.values() if p["stock"] < p["stock_minimo"])

            return {
                "success": True,
                "estadisticas": {
                    "productos": total_productos,
                    "stock_total": total_stock,
                    "valor_total": valor_total,
                    "bajo_stock": bajo_stock
                }
            }
        except Exception as e:
            return {"success": False, "message": f"Error obteniendo estadísticas: {str(e)}"}

    def healthCheck(self):
        """Verificar estado del servicio"""
        return {
            "success": True,
            "status": "healthy",
            "productos": len(self.productos),
            "requerimientos": len(self.requerimientos)
        }

    def cargarRequerimientosProductos(self):
        """Detecta productos con bajo stock y genera un pedido al módulo AtenciónProveedores."""
        try:
            productos_bajo_stock = [
                {"nombre": p["nombre"], "cantidad": (p["stock_minimo"] * 2)}
                for p in self.productos.values() if p["stock"] <= p["stock_minimo"]
            ]

            if not productos_bajo_stock:
                print("📦 No hay productos con bajo stock. No se genera requerimiento.")
                return {"status": "ok", "mensaje": "Inventario suficiente."}

            requerimiento = {
                "origen": "Inventario",
                "productos": productos_bajo_stock,
                "motivo": "Reabastecimiento automático por bajo stock"
            }

            print("\n📡 Enviando requerimiento a AtenciónProveedores...")
            print(json.dumps(requerimiento, indent=4, ensure_ascii=False))

            class CustomTransport(Transport):
                """Transporte XML-RPC personalizado que fuerza la ruta /rpc en lugar de /RPC2."""
                def request(self, host, handler, request_body, verbose=False):
                    # Forzar siempre el handler /rpc
                    handler = "/rpc"
                    return super().request(host, handler, request_body, verbose)



            proveedor_rpc = xmlrpc.client.ServerProxy(
                ATENCION_PROVEEDORES_RPC_URL,
                allow_none=True,
                transport=CustomTransport()
            )


            respuesta = proveedor_rpc.procesarRequerimiento(json.dumps(requerimiento))

            print(f"📥 Respuesta de AtenciónProveedores: {respuesta}")
            return {"status": "ok", "mensaje": "Requerimiento enviado correctamente."}

        except Exception as e:
            print(f"❌ Error al enviar requerimiento: {e}")
            return {"status": "error", "detalle": str(e)}