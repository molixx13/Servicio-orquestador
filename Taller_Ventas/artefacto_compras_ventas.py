"""
Módulo: artefacto_compras_ventas
Autor: Molixx13
Descripción:
---------------
Este programa implementa un artefacto de COMPRAS y VENTAS para una tienda de muebles.
Funciona como un servicio RPC (Remote Procedure Call) que permite registrar ventas y compras.

El servicio permite:
- Registrar ventas realizadas por clientes (desde el módulo Tienda).
- Solicitar generación de facturas al módulo de Contabilidad.
- Recibir y almacenar facturas de contabilidad.
- Registrar compras realizadas a proveedores (desde el módulo AtenciónProveedores).
- Enviar las facturas de proveedores a contabilidad para su registro.

IMPORTANTE: Este módulo NO genera facturas. Las facturas son generadas ÚNICAMENTE
por el módulo de Contabilidad. Si Contabilidad no está disponible, se registra
el error y se continúa sin factura.

Arquitectura:
-------------
[Tienda] ---------> [Compras/Ventas] ---------> [Contabilidad]
                           ↑
[AtenciónProveedores] -----┘

Todo el sistema usa estructuras de datos simples (diccionarios) y notación JSON.
Está documentado de forma clara para que cualquiera pueda entender cómo funciona.
"""

# Importa la clase SimpleXMLRPCServer del módulo xmlrpc.server para crear el servidor RPC
from xmlrpc.server import SimpleXMLRPCServer
# Importa el módulo xmlrpc.client para crear clientes RPC que se conecten a otros servicios
import xmlrpc.client
# Importa el módulo json para serializar y deserializar datos en formato JSON
import json
# Importa el módulo socket para obtener información de red (IP, hostname)
import socket


# =========================
# CONFIGURACIÓN DE SERVICIOS
# =========================

# Dirección IP y puerto donde se encuentra el servicio de Contabilidad
# IMPORTANTE: Cambiar estos valores según donde esté corriendo el servicio de Contabilidad
IP_CONTABILIDAD = "25.21.199.213"  # Cambiar por la IP real del servidor de Contabilidad
PUERTO_CONTABILIDAD = 10010     # Puerto donde escucha el servicio de Contabilidad

# Puerto donde correrá este servicio de Compras/Ventas
PUERTO_COMPRAS_VENTAS = 9000


# =========================
# ESTRUCTURAS DE DATOS
# =========================

# Diccionario vacío para almacenar todas las ventas realizadas (clave: id_venta, valor: datos de la venta)
ventas = {}
# Diccionario vacío para almacenar todas las compras realizadas (clave: id_compra, valor: datos de la compra)
compras = {}
# Diccionario vacío para almacenar las facturas recibidas de Contabilidad (clave: id_transacción, valor: datos de factura)
facturas = {}


# =========================
# FUNCIONES DE CONEXIÓN RPC
# =========================

def conectar_con_contabilidad():
    """
    Establece una conexión RPC con el módulo de Contabilidad.
    
    Esta función crea un objeto cliente que permite llamar a métodos remotos
    del servicio de Contabilidad como si fueran funciones locales.
    
    Retorna:
    --------
    ServerProxy o None
        Objeto cliente para invocar métodos remotos de Contabilidad.
        Retorna None si hay error en la conexión.
    
    Ejemplo de uso:
    ---------------
    >>> contabilidad = conectar_con_contabilidad()
    >>> if contabilidad:
    >>>     factura = contabilidad.generar_factura(datos)
    """
    try:
        # Construye la URL completa del servicio de Contabilidad
        url_contabilidad = f"http://{IP_CONTABILIDAD}:{PUERTO_CONTABILIDAD}"
        # Crea y retorna el objeto cliente RPC
        cliente_contabilidad = xmlrpc.client.ServerProxy(url_contabilidad, allow_none=True)
        return cliente_contabilidad
    except Exception as e:
        # Si hay error en la conexión, imprime el mensaje y retorna None
        print(f"❌ Error al conectar con Contabilidad: {e}")
        return None


def solicitar_factura_a_contabilidad(tipo, entidad, total, productos):
    """
    Solicita al módulo de Contabilidad (PLAN_C) que genere una factura oficial.
    Se adapta al formato y método que usa dicho servicio (generarFactura).
    """
    try:
        contabilidad = conectar_con_contabilidad()
        if contabilidad:
            print(f"📞 Solicitando factura a Contabilidad para {tipo}...")

            # Construcción del JSON según PLAN_C
            datos = {
                "tipo_operacion": tipo.upper(),  # "VENTA" o "COMPRA"
                "nombre_cliente": entidad,
                "productos": [
                    {"id": p, "cantidad": 1, "precio_unit": total / len(productos)}
                    for p in productos
                ],
                "total": total,
                "fecha": "2025-10-24T15:00:00"
            }

            # Convertir a string JSON
            json_data = json.dumps(datos)

            # Llamar al método remoto correcto
            respuesta_json = contabilidad.generarFactura(json_data)

            # Convertir la respuesta JSON (string) a diccionario
            factura = json.loads(respuesta_json)

            print("✅ Factura recibida desde Contabilidad")
            return factura
        else:
            print("⚠️ No se pudo conectar con Contabilidad.")
            return None

    except Exception as e:
        print(f"❌ Error al solicitar factura a Contabilidad: {e}")
        return None


def enviar_factura_a_contabilidad(factura):
    """
    Envía una factura del proveedor al módulo de Contabilidad (PLAN_C).
    Se adapta para usar el método recibirFactura(json_data) con string JSON.
    """
    try:
        contabilidad = conectar_con_contabilidad()
        if contabilidad:
            print(f"📤 Enviando factura de {factura['tipo']} a Contabilidad...")

            # Convertir el diccionario a string JSON
            json_data = json.dumps(factura)

            # Enviar al método recibirFactura()
            resultado = contabilidad.recibirFactura(json_data)
            print(f"✅ Factura registrada en Contabilidad: {resultado}")
            return True
        else:
            print("⚠️ No se pudo conectar con Contabilidad. Factura no enviada.")
            print(f"📋 Factura pendiente: {json.dumps(factura, indent=4, ensure_ascii=False)}")
            return False

    except Exception as e:
        print(f"❌ Error al enviar factura a Contabilidad: {e}")
        print(f"📋 Datos no enviados: {json.dumps(factura, indent=4, ensure_ascii=False)}")
        return False


# =========================
# FUNCIONES DEL SERVICIO
# =========================

def registrar_venta(cliente, productos, total):
    # Si el cliente envió un solo argumento tipo dict o JSON
    if isinstance(cliente, dict):
        datos = cliente
        cliente = datos.get("cliente", "Cliente desconocido")
        productos = datos.get("productos", ["Producto"])
        total = datos.get("total", 0.0)
        print("🧾 Recibida venta estructurada desde cliente externo:", cliente)
    elif isinstance(cliente, str) and productos is None and total is None:
        # Si llega un solo string (posiblemente JSON)
        try:
            datos = json.loads(cliente)
            cliente = datos.get("cliente", "Cliente desconocido")
            productos = datos.get("productos", ["Producto"])
            total = datos.get("total", 0.0)
            print("🧾 Recibida venta JSON desde cliente externo:", cliente)
        except Exception:
            print("⚠️ Error: formato desconocido recibido por registrar_venta()")
            return json.dumps({"error": "Formato de datos inválido"})

    # --- Resto de la lógica original ---
    venta_id = len(ventas) + 1
    ventas[venta_id] = {
        "cliente": cliente,
        "productos": productos,
        "total": total
    }

    print(f"\n💰 Nueva venta registrada:")
    print(f"   ID: {venta_id}")
    print(f"   Cliente: {cliente}")
    print(f"   Productos: {', '.join(productos)}")
    print(f"   Total: ${total:,.2f}")

    factura = solicitar_factura_a_contabilidad("venta", cliente, total, productos)
    factura_recibida = False

    if factura is not None:
        facturas[venta_id] = factura
        factura_recibida = True
        print(f"📄 Factura recibida y almacenada con ID: {venta_id}\n")
    else:
        print(f"⚠️  Venta registrada SIN factura (Contabilidad no disponible)\n")

    respuesta = {
        "mensaje": "Venta registrada exitosamente.",
        "id_venta": venta_id,
        "venta": ventas[venta_id],
        "factura": factura,
        "factura_recibida": factura_recibida
    }

    return json.dumps(respuesta, indent=4, ensure_ascii=False)



def registrar_compra(proveedor, productos, total):
    """
    Registra una compra de inventario realizada a un proveedor.
    
    Este método es invocado remotamente por el módulo de AtenciónProveedores cuando
    la empresa adquiere mercancía de un proveedor. El proceso incluye:
    1. Registrar la compra en el sistema local
    2. Recibir la factura del proveedor (como parámetro o generada)
    3. Enviar la factura a Contabilidad para su registro contable
    4. Retornar confirmación con todos los detalles
    
    Flujo de invocación:
    --------------------
    [Proveedor entrega mercancía] → [AtenciónProveedores llama registrar_compra via RPC] →
    [Compras/Ventas registra] → [Recibe factura proveedor] →
    [Envía factura a Contabilidad via RPC] → [Retorna confirmación a AtenciónProveedores]
    
    Parámetros:
    proveedor : str
        Nombre o razón social del proveedor que vende a la empresa.
        Ejemplo: "Maderera El Roble", "Fábrica de Tapizados Ltda"
    productos : list
        Lista de nombres de productos/materiales adquiridos del proveedor.
        Ejemplo: ["madera", "tornillos"], ["tela", "espuma", "resortes"]
    total : float
        Valor total de la compra en pesos colombianos.
        Ejemplo: 800000.0, 2350000.00
    
    Retorna:
    --------
    str (JSON)
        String en formato JSON con la confirmación de la compra registrada.
        Incluye: mensaje, id_compra, datos de la compra, y estado del envío a Contabilidad.
    
    Ejemplo de uso desde AtenciónProveedores (cliente RPC):
    ------------------------------------------------------
    >>> import xmlrpc.client
    >>> compras_ventas = xmlrpc.client.ServerProxy('http://192.168.1.10:9000')
    >>> respuesta = compras_ventas.registrar_compra("Maderera El Roble", ["madera", "tornillos"], 800000.0)
    >>> print(respuesta)
    {
        "mensaje": "Compra registrada exitosamente.",
        "id_compra": 1,
        "compra": {...},
        "enviada_a_contabilidad": true/false
    }
    """
    # Calcula el ID único de la nueva compra incrementando el contador actual
    compra_id = len(compras) + 1
    
    # Registra la compra en el diccionario local con toda su información
    compras[compra_id] = {
        "proveedor": proveedor,       # Nombre del proveedor vendedor
        "productos": productos,       # Lista de productos/materiales comprados
        "total": total                # Monto total de la compra
    }
    
    print(f"\n🛒 Nueva compra registrada:")
    print(f"   ID: {compra_id}")
    print(f"   Proveedor: {proveedor}")
    print(f"   Productos: {', '.join(productos)}")
    print(f"   Total: ${total:,.2f}")

    # Construye el objeto de factura del proveedor para enviar a Contabilidad
    # NOTA: En un sistema real, esta factura vendría del proveedor como documento físico/digital
    factura_proveedor = {
        "tipo": "compra",             # Tipo de transacción
        "entidad": proveedor,         # Nombre del proveedor
        "productos": productos,       # Lista de productos
        "total": total                # Monto total
    }
    print(f"📄 Datos de factura del proveedor preparados")

    # Envía la factura del proveedor al módulo de Contabilidad via RPC para su registro
    envio_exitoso = enviar_factura_a_contabilidad(factura_proveedor)
    
    if envio_exitoso:
        print(f"✅ Factura enviada exitosamente a Contabilidad\n")
    else:
        print(f"⚠️  Factura no pudo ser enviada a Contabilidad")
        print(f"⚠️  Debe sincronizar con Contabilidad cuando esté disponible\n")

    # Construye la respuesta en formato diccionario con toda la información
    respuesta = {
        "mensaje": "Compra registrada exitosamente.",  # Mensaje de confirmación
        "id_compra": compra_id,                        # ID único asignado a la compra
        "compra": compras[compra_id],                  # Datos completos de la compra
        "factura_proveedor": factura_proveedor,        # Datos de la factura del proveedor
        "enviada_a_contabilidad": envio_exitoso        # Indica si se envió a Contabilidad
    }
    
    # Convierte el diccionario a formato JSON con indentación y lo retorna
    return json.dumps(respuesta, indent=4, ensure_ascii=False)


def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip



def consultar_ventas():
    """
    Retorna todas las ventas registradas en el sistema.
    
    Método auxiliar para consultar el historial completo de ventas.
    Útil para reportes, auditorías o sincronización de datos.
    
    Retorna:
    --------
    str (JSON)
        String JSON con el diccionario completo de ventas.
    """
    # Convierte el diccionario de ventas a formato JSON y lo retorna
    return json.dumps(ventas, indent=4, ensure_ascii=False)


def consultar_compras():
    """
    Retorna todas las compras registradas en el sistema.
    
    Método auxiliar para consultar el historial completo de compras a proveedores.
    Útil para reportes, auditorías o sincronización de datos.
    
    Retorna:
    --------
    str (JSON)
        String JSON con el diccionario completo de compras.
    """
    # Convierte el diccionario de compras a formato JSON y lo retorna
    return json.dumps(compras, indent=4, ensure_ascii=False)


def consultar_facturas():
    """
    Retorna todas las facturas almacenadas en el sistema.
    
    NOTA: Solo contiene facturas que fueron recibidas exitosamente de Contabilidad.
    Las ventas sin factura no aparecerán aquí.
    
    Método auxiliar para consultar el historial completo de facturas.
    Útil para reportes, auditorías o sincronización de datos.
    
    Retorna:
    --------
    str (JSON)
        String JSON con el diccionario completo de facturas recibidas de Contabilidad.
    """
    # Convierte el diccionario de facturas a formato JSON y lo retorna
    return json.dumps(facturas, indent=4, ensure_ascii=False)


# =========================
# SERVIDOR RPC
# =========================

def iniciar_servidor():
    """
    Inicia el servidor RPC que expone todas las funciones del artefacto Compras/Ventas.
    
    Este servidor queda escuchando permanentemente en un puerto específico,
    esperando que otros módulos (Tienda, AtenciónProveedores) se conecten
    y llamen a los métodos registrados de forma remota.
    
    Métodos expuestos via RPC:
    --------------------------
    - registrar_venta(cliente, productos, total)
      Llamado por el módulo Tienda cuando un cliente compra.
      
    - registrar_compra(proveedor, productos, total)
      Llamado por el módulo AtenciónProveedores cuando se compra a un proveedor.
      
    - obtener_ip_local()
      Retorna la IP del servidor para facilitar conexiones.
      
    - consultar_ventas()
      Retorna el historial completo de ventas.
      
    - consultar_compras()
      Retorna el historial completo de compras.
      
    - consultar_facturas()
      Retorna el historial completo de facturas recibidas de Contabilidad.
    
    Configuración:
    --------------
    - IP: Se obtiene automáticamente de la red local
    - Puerto: Definido en la constante PUERTO_COMPRAS_VENTAS (9000)
    - Protocolo: XML-RPC sobre HTTP
    - Formato de datos: JSON
    
    Arquitectura de conexión:
    -------------------------
    [Módulo Tienda] ----RPC----> [Este Servidor] ----RPC----> [Contabilidad]
                                        ↑
    [AtenciónProveedores] ----RPC------┘
    
    Ejecución:
    ----------
    Este servidor se ejecuta en un bucle infinito (serve_forever) y no termina
    hasta que se detenga manualmente (Ctrl+C) o se mate el proceso.
    
    Retorna:
    --------
    None
        Esta función no retorna. Se ejecuta indefinidamente hasta ser detenida.
    
    Ejemplo de conexión desde otros módulos:
    ----------------------------------------
    >>> import xmlrpc.client
    >>> # Desde el módulo Tienda o AtenciónProveedores
    >>> servidor_compras_ventas = xmlrpc.client.ServerProxy('http://192.168.1.10:9000')
    >>> respuesta = servidor_compras_ventas.registrar_venta("Cliente", ["producto"], 100000)
    """
    # Obtiene la dirección IP local de la máquina donde corre el servidor
    ip = obtener_ip_local()
    # Usa el puerto definido en la configuración global
    puerto = PUERTO_COMPRAS_VENTAS
    
    # Define en qué interfaz escuchará el servidor
    # '0.0.0.0' = Escucha en TODAS las interfaces de red (permite conexiones remotas)
    # 'localhost' = Solo conexiones locales (misma máquina)
    # ip = Solo la IP específica de la red
    host_escucha = '0.0.0.0'  # IMPORTANTE: Permite conexiones desde otras computadoras

    # Imprime banner informativo con los datos de conexión del servidor
    print("\n" + "="*60)
    print("🚀 SERVIDOR COMPRAS/VENTAS INICIADO")
    print("="*60)
    print(f"📍 IP de esta máquina:  {ip}")
    print(f"🔌 Puerto:              {puerto}")
    print(f"🌐 URL para conexión:   http://{ip}:{puerto}")
    print(f"🔓 Escuchando en:       {host_escucha} (todas las interfaces)")
    print(f"📡 Protocolo:           XML-RPC")
    print(f"📄 Formato de datos:    JSON")
    print("="*60)
    print("\n📋 MÉTODOS DISPONIBLES VIA RPC:")
    print("   • registrar_venta(cliente, productos, total)")
    print("   • registrar_compra(proveedor, productos, total)")
    print("   • obtener_ip_local()")
    print("   • consultar_ventas()")
    print("   • consultar_compras()")
    print("   • consultar_facturas()")
    print("="*60)
    print(f"\n🔗 CONECTANDO CON:")
    print(f"   Contabilidad → http://{IP_CONTABILIDAD}:{PUERTO_CONTABILIDAD}")
    print("="*60)
    print("\n⚠️  NOTA IMPORTANTE:")
    print("   Este módulo NO genera facturas.")
    print("   Las facturas son generadas ÚNICAMENTE por Contabilidad.")
    print("="*60)
    print("\n💡 CONEXIÓN DESDE OTRAS COMPUTADORAS:")
    print(f"   Los otros módulos deben conectarse a:")
    print(f"   http://{ip}:{puerto}")
    print("="*60)
    print("\n⏳ Esperando llamadas RPC...\n")

    # Crea la instancia del servidor RPC escuchando en TODAS las interfaces (0.0.0.0)
    # Esto permite que otras computadoras en la red se puedan conectar
    # allow_none=True permite transmitir valores None via RPC
    servidor = SimpleXMLRPCServer((host_escucha, puerto), allow_none=True)
    
    # Registra cada función para que pueda ser invocada remotamente
    # El primer parámetro es la función local, el segundo es el nombre expuesto via RPC
    servidor.register_function(registrar_venta, "registrar_venta")
    servidor.register_function(registrar_compra, "registrar_compra")
    servidor.register_function(obtener_ip_local, "obtener_ip_local")
    servidor.register_function(consultar_ventas, "consultar_ventas")
    servidor.register_function(consultar_compras, "consultar_compras")
    servidor.register_function(consultar_facturas, "consultar_facturas")

    # Inicia el servidor en un bucle infinito
    # Quedará esperando y procesando llamadas RPC hasta que se detenga manualmente
    servidor.serve_forever()


# =========================
# EJECUCIÓN PRINCIPAL
# =========================

# Verifica si el script se está ejecutando directamente (no importado como módulo)
if __name__ == "__main__":
    try:
        # Llama a la función para iniciar el servidor RPC
        iniciar_servidor()
    except KeyboardInterrupt:
        # Captura la interrupción por teclado (Ctrl+C) para cerrar gracefully
        print("\n\n🛑 Servidor detenido por el usuario")
        print("👋 ¡Hasta pronto!\n")
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"\n❌ Error fatal en el servidor: {e}\n")