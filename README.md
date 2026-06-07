# 🛍️ Servicio Orquestador - Tienda de Muebles

Sistema de microservicios para gestionar operaciones de una tienda de muebles mediante comunicación RPC distribuida.

## 📋 Descripción General

Este proyecto implementa una arquitectura de **microservicios independientes** que se comunican mediante **XML-RPC** para coordinar operaciones de ventas, inventario, contabilidad y logística. Cada servicio es responsable de un dominio específico del negocio.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              CLIENTE (Tienda.py)                        │
│  • Interfaz interactiva para ventas                     │
│  • Gestión de inventario                               │
└────────────────┬────────────────┬──────────────────────┘
                 │                │
        ┌────────▼────────┐  ┌────▼──────────────┐
        │  INVENTARIO     │  │  COMPRAS/VENTAS   │
        │  (Puerto 8010)  │  │  (Puerto 9000)    │
        │  • Stock        │  │  • Ordena Txns    │
        │  • Productos    │  │  • Historial      │
        └────────┬────────┘  └────┬──────────────┘
                 │                │
                 └────────┬───────┘
                          │
            ┌─────────────▼──────────────┐
            │  CONTABILIDAD              │
            │  (Puerto 10010)            │
            │  • Facturas (ASYNC)        │
            │  • Asientos contables      │
            │  • Actualiza Inventario    │
            └─────────────┬──────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐    ┌────────────┐    ┌─────────────┐
    │Proveed.│    │Transportad.│    │Taller Ventas│
    │(Docs)  │    │(Puerto 7000)│    │(Reportes)   │
    └────────┘    └────────────┘    └─────────────┘
```

## 🔧 Módulos Principales

### 1. **Inventario** (`inventario/`) - Puerto 8010
**Responsabilidades:**
- Gestionar productos y stock en tiempo real
- Actualizar cantidades tras ventas y compras
- Generar estadísticas de inventario

**Archivos clave:**
- `inventario_server.py` - Servidor RPC con persistencia
- `inventario_service.py` - Lógica de negocio
- `inventario_data.json` - Almacenamiento de datos

**Métodos RPC:** `cargarProductos`, `actualizarInventario`, `listarProductos`, `estadisticasInventario`

---

### 2. **Compras/Ventas** (`Taller_Ventas/`) - Puerto 9000
**Responsabilidades:**
- Registrar transacciones de venta
- Registrar compras a proveedores
- Coordinar con Contabilidad

**Archivos clave:**
- `artefacto_compras_ventas.py` - Servicio RPC multihilo
- Comunicación sincrónica con timeout (90s)
- Thread-safe con locks

**Métodos RPC:** `registrar_venta`, `registrar_compra`, `consultar_ventas`, `consultar_compras`, `consultar_facturas`

---

### 3. **Contabilidad** (`contabilidad/`) - Puerto 10010
**Responsabilidades:**
- Generar facturas oficiales
- Crear asientos contables
- **ÚNICA RESPONSABLE** de actualizar inventario (evita duplicación)

**Arquitectura asíncrona:**
- Worker thread procesa actualizaciones de inventario en segundo plano
- Respuestas instantáneas al cliente (<2 segundos)
- Cola (Queue) para ordenar actualizaciones

**Archivos clave:**
- `contabilidadRPC.py` - Servidor con procesamiento asíncrono

**Métodos RPC:** `generarFactura`, `recibirFactura`

---

### 4. **Tienda (Cliente)** (`Tienda/`) - Interfaz Usuario
**Responsabilidades:**
- Proporcionar interfaz interactiva
- Gestionar inventario desde cliente
- Procesar compras de clientes

**Archivos clave:**
- `Tienda.py` - Cliente interactivo RPC

**Modos:**
- 🛒 **Modo Compras:** Simula ventas en tiempo real
- 🧩 **Modo Inventario:** Gestión de productos

---

### 5. **Proveedores** (`Provedores/`)
- Gestión de relaciones con proveedores
- Historial de compras

---

### 6. **Transportadora** (`Transportadora/`) - Puerto 7000
- Gestión de envíos y logística

---

## ⚙️ Flujo de una Venta (End-to-End)

```
1. Cliente selecciona producto en Tienda.py
   ↓
2. Tienda envía: registrar_venta() → Compras/Ventas (9000)
   ↓
3. Compras/Ventas guarda txn y solicita: generarFactura() → Contabilidad (10010)
   ↓
4. Contabilidad ENCOLA actualización de inventario (ASYNC)
   ↓
5. Contabilidad responde INMEDIATAMENTE con factura
   ↓
6. [Paralelo] Worker actualiza Inventario en segundo plano
   ↓
7. Inventario disminuye stock → persistencia en JSON
```

## 🔄 Procesamiento Asíncrono (Contabilidad)

Para evitar timeouts y bloqueos:

```python
# Contabilidad NO espera actualizar inventario
# Encola la tarea: queue_inventario.put((tipo, datos, id))
# Worker thread procesa en paralelo

while True:
    tarea = queue_inventario.get()  # Espera tareas
    respuesta = inventario_rpc.actualizarInventario(json.dumps(datos))
    # Maneja errores y logs
```

**Beneficios:**
- ✅ Respuestas inmediatas (<1 seg)
- ✅ Evita deadlocks entre servicios
- ✅ Calidad de servicio predecible

---

## 🚀 Cómo Ejecutar

### Requisitos
- Python 3.8+
- Sin dependencias externas (usa stdlib: `xmlrpc`, `json`, `threading`)

### Iniciar Servicios (en terminales separadas)

```bash
# Terminal 1: Inventario (8010)
cd inventario
python inventario_server.py

# Terminal 2: Compras/Ventas (9000)
cd Taller_Ventas
python artefacto_compras_ventas.py

# Terminal 3: Contabilidad (10010)
cd contabilidad
python contabilidadRPC.py

# Terminal 4: Cliente Interactivo
cd Tienda
python Tienda.py
```

## 📡 Configuración de Red

Editar URLs en archivos según tu red local:

```python
# Tienda.py
INVENTARIO_RPC_URL = "http://25.21.199.213:8010/rpc"
COMPRAS_RPC_URL = "http://192.168.100.233:9000/rpc"
TRANSPORTADOR_RPC_URL = "http://25.21.199.213:7000"
```

## 🎯 Principios de Diseño

| Principio | Implementación |
|-----------|----------------|
| **Responsabilidad Única** | Cada servicio tiene un dominio específico |
| **Comunicación Asíncrona** | Contabilidad procesa actualizaciones en paralelo |
| **Sin Duplicación** | Solo Contabilidad actualiza inventario |
| **Thread-Safe** | Locks (mutex) para estructuras compartidas |
| **Tolerancia a Fallos** | Registros locales + respuestas parciales |
| **Timeouts** | 90 segundos para evitar bloqueos indefinidos |

## 📊 Formato de Datos

### Venta
```json
{
  "tipo_operacion": "VENTA",
  "nombre_cliente": "Juan Pérez",
  "productos": [
    {
      "nombre": "Mesa",
      "cantidad": 1,
      "precio_unit": 100000
    }
  ],
  "total": 100000
}
```

### Compra
```json
{
  "tipo": "COMPRA",
  "proveedor": "MueblesXYZ",
  "productos": ["Mesa", "Silla"],
  "total": 500000,
  "compra_id": 1,
  "fecha": "2025-11-05 14:30:00"
}
```

## 🔍 Estado Actual

- ✅ Servicios core funcionales (Inventario, Compras/Ventas, Contabilidad)
- ✅ Comunicación RPC estable
- ✅ Procesamiento asíncrono implementado
- ⏳ Documentación modular en cada carpeta
- 📋 Persistencia en JSON (no usar en producción)

## 📝 Notas

- Los servicios usan **direcciones IP hardcodeadas** (requiere configuración local)
- Datos persisten en **archivos JSON** (preferir base de datos en producción)
- Sin autenticación implementada (agregar en producción)
- Sin manejo de excepciones de red robusto

---

**Autor:** Molixx13 | **Versión:** 2.0 | **Fecha:** Noviembre 2025
