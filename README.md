# Monitor de Operaciones Retail

Proyecto desarrollado para integrar conceptos básicos de backend, bases de datos, APIs y automatización.

El sistema permite gestionar productos y ventas, controlar el stock, generar alertas, calcular métricas e integrar información proveniente de una API externa.

## Tecnologías utilizadas

- Python
- FastAPI
- PostgreSQL
- n8n
- Git y GitHub

## Arquitectura

El proyecto sigue un flujo simple:

Cliente → FastAPI → PostgreSQL

FastAPI funciona como backend y expone una API REST. PostgreSQL almacena los productos y las ventas de forma persistente.

Además, el sistema se integra con:

- Una API externa de productos, cuyos datos pueden ser consultados e importados al sistema.
- n8n, que consulta periódicamente las alertas de stock y procesa los productos con stock crítico o sin stock.

## Endpoints principales

### Productos

- `GET /productos` → lista todos los productos.
- `GET /productos/{producto_id}` → obtiene un producto por su ID.
- `POST /productos` → crea un producto.
- `PATCH /productos/{producto_id}` → actualiza un producto.
- `DELETE /productos/{producto_id}` → elimina un producto.

### Ventas

- `GET /ventas` → lista las ventas registradas.
- `POST /ventas` → registra una venta y descuenta automáticamente el stock del producto.

### Alertas

- `GET /alertas/stock` → devuelve los productos sin stock o con stock crítico.

### Métricas

- `GET /metricas/facturacion` → calcula la facturación total.
- `GET /metricas/unidades-vendidas` → calcula la cantidad total de unidades vendidas.
- `GET /metricas/ventas-por-producto` → agrupa las unidades vendidas por producto.
- `GET /metricas/valor-inventario` → calcula el valor monetario del stock actual.

### Integración externa

- `GET /productos-externos` → consulta productos de una API externa.
- `POST /productos-externos/{producto_id}` → importa un producto externo a PostgreSQL.

## Ejecución del proyecto

### 1. Clonar el repositorio

```bash
git clone <https://github.com/marcomol-cyber/monitor-operaciones-retail.git>
cd monitor-operaciones-retail
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crear un archivo `.env` tomando como referencia `.env.example` y completar la contraseña local de PostgreSQL.

### 5. Crear la base de datos

Crear en PostgreSQL una base llamada:

```text
monitor_operaciones_retail
```

Luego ejecutar:

```bash
psql -U postgres -d monitor_operaciones_retail -f sql/esquema.sql
```

### 6. Iniciar la API

```bash
fastapi dev backend/main.py
```

La documentación interactiva de la API queda disponible mediante Swagger en `/docs`.

### 7. Automatización con n8n

El workflow utilizado para monitorear las alertas de stock se encuentra en:

```text
n8n/alertas-stock.json
```

Puede importarse en una instalación local de n8n.

## Limitaciones y posibles mejoras

El proyecto mantiene una arquitectura simple.

Algunas posibles mejoras futuras son:

- Agregar un manejo de errores más completo.
- Incorporar autenticación y usuarios.
- Agregar tests automatizados.
- Mejorar el manejo de identificadores al importar productos externos.
- Incorporar una interfaz visual para consultar métricas y alertas.