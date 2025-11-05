"""
Módulo: transportador.py
Autor: Molixx13
Descripción:
------------
Servicio XML-RPC que gestiona el transporte y entrega de productos vendidos.
Recibe las órdenes de envío desde el módulo Tienda (cliente RPC) o desde Compras/Ventas,
almacena los datos de cada envío en un archivo JSON local y devuelve confirmación.
"""

from xmlrpc.server import SimpleXMLRPCServer
import json
import os
import socket
from datetime import datetime

# ===========================================================
# CONFIGURACIÓN DE RED Y ARCHIVO
# ===========================================================
hostIP = str(socket.gethostbyname(socket.gethostname()))
port = 7000
DATA_FILE = "envios_data.json"

# ===========================================================
# FUNCIONES AUXILIARES
# ===========================================================
def cargar_envios():
    """Carga el archivo JSON de envíos (o crea uno nuevo si no existe)."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_envios(envios):
    """Guarda la lista de envíos actualizada en el archivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(envios, f, indent=4, ensure_ascii=False)

def banner_inicio():
    print("=" * 70)
    print("🚚 SERVIDOR TRANSPORTADOR INICIADO")
    print("=" * 70)
    print(f"📍 IP de esta máquina:  {hostIP}")
    print(f"🔌 Puerto:              {port}")
    print(f"🌐 URL para conexión:   http://{hostIP}:{port}/rpc")
    print(f"📡 Protocolo:           XML-RPC")
    print("=" * 70)
    print("\n📋 MÉTODOS DISPONIBLES VIA RPC:")
    print("   • ordenarTransporte(json_data)")
    print("      └─ Registra un nuevo envío de productos vendidos.")
    print("   • listarEnvios()")
    print("      └─ Devuelve todos los envíos registrados.")
    print("=" * 70)
    print("\n⏳ Esperando llamadas RPC...\n")

# ===========================================================
# CLASE PRINCIPAL DEL SERVICIO
# ===========================================================
class ServidorTransportador:
    """Servicio RPC que gestiona los envíos de productos vendidos."""

    def ordenarTransporte(self, json_data):
        """
        Recibe los datos de un pedido y registra un nuevo envío.
        json_data → JSON con: cliente, producto, cantidad, total
        """
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            elif isinstance(json_data, dict):
                data = json_data
            else:
                raise ValueError("Formato de datos no reconocido")

            cliente = data.get("cliente", "Desconocido")
            producto = data.get("producto", "N/A")
            cantidad = data.get("cantidad", 0)
            total = data.get("total", 0)

            print("="*70)
            print("🚚 NUEVA ORDEN DE TRANSPORTE RECIBIDA")
            print("="*70)
            print(f"👤 Cliente: {cliente}")
            print(f"🪑 Producto: {producto}")
            print(f"📦 Cantidad: {cantidad}")
            print(f"💰 Total: ${total:,.0f}")
            print(f"⏰ Fecha registro: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Cargar y registrar envío
            envios = cargar_envios()
            envio = {
                "cliente": cliente,
                "producto": producto,
                "cantidad": cantidad,
                "total": total,
                "estado": "Despachado",
                "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            envios.append(envio)
            guardar_envios(envios)

            print(f"💾 Envío registrado en {os.path.abspath(DATA_FILE)}")
            print("✅ Transporte confirmado.\n")
            return {"status": "ok", "mensaje": "Transporte ordenado correctamente."}

        except Exception as e:
            print(f"❌ Error al registrar transporte: {e}")
            return {"status": "error", "detalle": str(e)}

    def listarEnvios(self):
        """Devuelve todos los envíos registrados."""
        envios = cargar_envios()
        return {"total": len(envios), "data": envios}

# ===========================================================
# SERVIDOR PRINCIPAL
# ===========================================================
if __name__ == "__main__":
    server = SimpleXMLRPCServer((hostIP, port), allow_none=True)
    server.register_instance(ServidorTransportador())
    banner_inicio()
    server.serve_forever()
