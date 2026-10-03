#Imports
import os
import psycopg
import requests
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

#Configuración de la API
app = FastAPI(
    title="Monitor de Operaciones Retail",
    description="API para monnitorear productos, stock y operaciones retail.",
    version="0.1.0"
)
class Producto(BaseModel):
    id: int
    nombre: str
    precio: float
    stock: int

class ActualizacionProducto(BaseModel):
    nombre: str | None = None
    precio: float | None = None
    stock: int | None = None

class Venta(BaseModel):
    id: int
    producto_id: int
    cantidad: int

#Funciones
def revisar_stock(stock):
    if stock == 0:
        return "SIN STOCK"
    elif stock < 5:
        return "STOCK CRÍTICO"
    else:
        return "STOCK NORMAL"

def obtener_conexion():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )    


#Endpoints
@app.get("/alertas/stock")
def obtener_alertas_stock():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("SELECT * FROM productos;")
    productos_db = cursor.fetchall()

    cursor.close()
    conexion.close()

    alertas = []

    for producto in productos_db:
        estado = revisar_stock(producto["stock"])

        if estado != "STOCK NORMAL":
            alertas.append({
                "id": producto["id"],
                "nombre": producto["nombre"],
                "stock": producto["stock"],
                "estado": estado
            })

    return alertas

@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute(
        "SELECT * FROM productos WHERE id = %s;",
        (producto_id,)
    )

    producto = cursor.fetchone()

    cursor.close()
    conexion.close()

    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto

@app.get("/productos")
def obtener_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("SELECT * FROM productos ORDER BY id;")
    productos_db = cursor.fetchall()

    cursor.close()
    conexion.close()

    return productos_db

@app.get("/ventas")
def obtener_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("SELECT * FROM ventas;")
    ventas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ventas

@app.get("/metricas/facturacion")
def obtener_facturacion():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("""
        SELECT SUM(ventas.cantidad * productos.precio) AS facturacion_total
        FROM ventas
        JOIN productos
            ON ventas.producto_id = productos.id;
    """)

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado

@app.get("/metricas/valor-inventario")
def obtener_valor_inventario():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("""
        SELECT SUM(precio * stock) AS valor_inventario
        FROM productos;
    """)

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado

@app.get("/metricas/ventas-por-producto")
def obtener_ventas_por_producto():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute("""
        SELECT productos.nombre, SUM(ventas.cantidad) AS unidades_vendidas
        FROM ventas
        JOIN productos
            ON ventas.producto_id = productos.id
        GROUP BY productos.nombre;
    """)

    resultado = cursor.fetchall()

    cursor.close()
    conexion.close()

    return resultado

@app.get("/productos-externos")
def obtener_productos_externos():
    respuesta = requests.get("https://dummyjson.com/products?limit=3")
    datos = respuesta.json()

    productos_externos = []

    for producto in datos["products"]:
        productos_externos.append({
            "id": producto["id"],
            "nombre": producto["title"],
            "precio": producto["price"],
            "stock": producto["stock"]
        })

    return productos_externos

@app.get("/metricas/valor_inventario")
def obtener_valor_inventario():
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute(""" 
        SELECT SUM(precio * stock) AS valor_inventario
        FROM productos;)
    """)

    resultado = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resultado

@app.post("/productos")
def crear_producto(producto: Producto):
    if producto.precio < 0:
        raise HTTPException(
            status_code=400,
            detail="El precio no puede ser negativo"
    )

    if producto.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="El stock no puede ser negativo"
    )
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO productos (id, nombre, precio, stock) VALUES (%s, %s, %s, %s);",
        (producto.id, producto.nombre, producto.precio, producto.stock)
    )

    conexion.commit()

    cursor.close()
    conexion.close()
    return producto

@app.post("/ventas")
def crear_venta(venta: Venta):
    if venta.cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor que 0"
        )
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute(
        "SELECT * FROM productos WHERE id = %s;",
        (venta.producto_id,)
    )
    producto = cursor.fetchone()

    if producto is None:
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto["stock"] < venta.cantidad:
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    cursor.execute(
        "INSERT INTO ventas (id, producto_id, cantidad, fecha) VALUES (%s, %s, %s, CURRENT_TIMESTAMP);",
        (venta.id, venta.producto_id, venta.cantidad)
    )

    cursor.execute(
        "UPDATE productos SET stock = stock - %s WHERE id = %s;",
        (venta.cantidad, venta.producto_id)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    return venta

@app.post("/productos-externos/{producto_id}")
def importar_producto(producto_id: int):
    respuesta = requests.get(
        f"https://dummyjson.com/products/{producto_id}"
    )

    producto_externo = respuesta.json()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO productos (id, nombre, precio, stock) VALUES (%s, %s, %s, %s);",
        (
            producto_externo["id"] + 1000,
            producto_externo["title"],
            producto_externo["price"],
            producto_externo["stock"]
        )
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return {"mensaje": "Producto externo importado correctamente"}


@app.patch("/productos/{producto_id}")
def actualizar_producto(producto_id: int, cambios: ActualizacionProducto):
    conexion = obtener_conexion()
    cursor = conexion.cursor(row_factory=dict_row)

    cursor.execute(
        "SELECT * FROM productos WHERE id = %s;",
        (producto_id,)
    )
    producto = cursor.fetchone()

    if producto is None:
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if cambios.nombre is not None:
        producto["nombre"] = cambios.nombre

    if cambios.precio is not None:
        producto["precio"] = cambios.precio

    if cambios.stock is not None:
        producto["stock"] = cambios.stock

    cursor.execute(
        "UPDATE productos SET nombre = %s, precio = %s, stock = %s WHERE id = %s;",
        (
            producto["nombre"],
            producto["precio"],
            producto["stock"],
            producto_id
        )
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return producto


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id = %s;",
        (producto_id,)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return {"mensaje": "Producto eliminado correctamente"}