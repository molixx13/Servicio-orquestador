import xmlrpc.client
import os
import sys
import json
import http.client
# ==============================
# CONFIGURACIÓN DE CONEXIONES
# ==============================
INVENTARIO_RPC_URL = "http://25.21.199.213:8010/rpc"
COMPRAS_RPC_URL = "http://192.168.100.233:9000/rpc"
TRANSPORTADOR_RPC_URL = "http://25.21.199.213:7000"  # 🚚 nuevo servicio

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

# ==============================
# MODO INVENTARIO (gestión)
# ==============================
def modo_inventario():
    limpiar()
    print("="*70)
    print("🧩 CLIENTE INTERACTIVO RPC - INVENTARIO")
    print("="*70)
    print("1. Listar productos")
    print("2. Agregar nuevo producto")
    print("3. Actualizar inventario")
    print("4. Ver estadísticas")
    print("5. Volver al menú principal")
    print("="*70)

    inventario_rpc = xmlrpc.client.ServerProxy(INVENTARIO_RPC_URL, allow_none=True)

    while True:
        try:
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                productos = inventario_rpc.listarProductos()
                if productos and "data" in productos:
                    print("\n🪑 PRODUCTOS DISPONIBLES:")
                    for p in productos["data"]:
                        print(f" - [ID {p['id']}] {p['nombre']} ({p['stock']} unidades, ${p['precio']:,.0f})")
                    print(f"\n📦 Total: {productos['total_productos']} productos\n")
                else:
                    print("⚠️ No se encontraron productos o error en respuesta.")
                input("Presiona ENTER para continuar...")

            elif opcion == "2":
                nombre = input("Nombre del producto: ")
                descripcion = input("Descripción: ")
                categoria = input("Categoría: ")
                precio = float(input("Precio: "))
                stock = int(input("Stock inicial: "))
                stock_minimo = int(input("Stock mínimo (por defecto 5): ") or 5)

                resultado = inventario_rpc.cargarProductos(nombre, descripcion, categoria, precio, stock, stock_minimo)
                print(f"✅ {resultado.get('message', 'Producto agregado correctamente.')}")
                input("Presiona ENTER para continuar...")

            elif opcion == "3":
                pid = input("ID del producto a actualizar: ").strip()
                nuevo_stock = int(input("Nuevo stock: "))
                nuevo_precio = float(input("Nuevo precio (0 para mantener): "))
                data = {
                    "producto_id": pid,
                    "stock": nuevo_stock,
                    "precio": nuevo_precio if nuevo_precio > 0 else None,
                    "tipo_operacion": "ACTUALIZACION"
                }
                resultado = inventario_rpc.actualizarInventario(data)
                print(f"✅ {resultado.get('message', 'Inventario actualizado.')}")
                input("Presiona ENTER para continuar...")

            elif opcion == "4":
                stats = inventario_rpc.estadisticasInventario()
                if stats and "estadisticas" in stats:
                    e = stats["estadisticas"]
                    print("\n📊 ESTADÍSTICAS DEL INVENTARIO")
                    print(f"🪑 Productos totales: {e['total_productos']}")
                    print(f"📦 Stock total: {e['total_stock']}")
                    print(f"💰 Valor total inventario: ${e['valor_total_inventario']:,.0f}")
                    print(f"⚠️ Productos con bajo stock: {e['productos_bajo_stock']}")
                else:
                    print("❌ Error en ver_estadisticas.")
                input("Presiona ENTER para continuar...")

            elif opcion == "5":
                print("🔙 Volviendo al menú principal...\n")
                break

            else:
                print("⚠️ Opción inválida.")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("Presiona ENTER para continuar...")

# ==============================
# MODO COMPRAS (ventas reales)
# ==============================
def modo_compras():
    limpiar()
    print("="*70)
    print("🛒 MODO COMPRAS - SIMULACIÓN DE VENTAS")
    print("="*70)

    try:
        inventario_rpc = xmlrpc.client.ServerProxy(INVENTARIO_RPC_URL, allow_none=True)
        compras_rpc = xmlrpc.client.ServerProxy(COMPRAS_RPC_URL, allow_none=True)
        transportador_rpc = xmlrpc.client.ServerProxy(TRANSPORTADOR_RPC_URL, allow_none=True)

        print("\n📦 Solicitando lista de productos disponibles...")
        inventario = inventario_rpc.listarProductos()

        if not inventario or "data" not in inventario or len(inventario["data"]) == 0:
            print("⚠️ No hay productos disponibles en el inventario.")
            return

        productos = inventario["data"]
        print("\n🪑 PRODUCTOS DISPONIBLES:")
        for p in productos:
            print(f" [{p['id']}] {p['nombre']} - ${p['precio']:,.0f} ({p['stock']} en stock)")

        id_producto = int(input("\n🆔 ID del producto a comprar: "))
        cantidad = int(input("📦 Cantidad a comprar: "))
        cliente = input("👤 Nombre del cliente: ")

        producto = next((p for p in productos if p["id"] == id_producto), None)
        if not producto:
            print("❌ Producto no encontrado.")
            return

        total = producto["precio"] * cantidad

        # Registro de la venta
        print("\n📡 Enviando venta a Compras/Ventas...")
        venta = compras_rpc.registrar_venta(
            cliente,
            [f"{producto['nombre']} x{cantidad}"],
            total
        )

        print("\n✅ Compra registrada correctamente.")
        print(f"🪑 Producto: {producto['nombre']}")
        print(f"📦 Cantidad: {cantidad}")
        print(f"💵 Total: ${total:,.0f}")

        # 🚚 Envío automático al transportador
        print("\n🚚 Solicitando transporte...")
        envio_data = json.dumps({
            "cliente": cliente,
            "producto": producto["nombre"],
            "cantidad": cantidad,
            "total": total
        })
        respuesta_envio = transportador_rpc.ordenarTransporte(envio_data)
        print(f"📦 Respuesta del transportador: {respuesta_envio}")

    except Exception as e:
        print(f"❌ Error en conexión o venta: {e}")

    input("\nPresiona ENTER para volver al menú principal...")

# ==============================
# MENÚ PRINCIPAL
# ==============================
def menu_principal():
    limpiar()
    print("="*70)
    print("🛍️ CLIENTE RPC - TIENDA DE MUEBLES")
    print("="*70)
    print("1. 🛒 Modo COMPRAS (ventas reales)")
    print("2. 🧩 Modo INVENTARIO (gestión)")
    print("3. 🚪 Salir")
    print("="*70)

    while True:
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            modo_compras()
            limpiar()
        elif opcion == "2":
            modo_inventario()
            limpiar()
        elif opcion == "3":
            print("👋 Saliendo del cliente RPC...")
            sys.exit(0)
        else:
            print("⚠️ Opción inválida.")

# ==============================
# EJECUCIÓN PRINCIPAL
# ==============================
if __name__ == "__main__":
    try:
        limpiar()
        print(f"🛒 CONECTADO AL SERVIDOR DE INVENTARIO RPC\n🔗 Endpoint: {INVENTARIO_RPC_URL}")
        menu_principal()
    except KeyboardInterrupt:
        print("\n👋 Cliente cerrado manualmente.")


