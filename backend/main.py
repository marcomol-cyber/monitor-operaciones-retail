#Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

#Funciones
def revisar_stock(producto):
    if producto.stock == 0:
        return "SIN STOCK"
    elif producto.stock < 5:
        return "STOCK CRÍTICO"
    else:
        return "STOCK NORMAL"
    
#Datos
productos = [
    Producto(id=1, nombre="Café", precio=8000, stock=7),
    Producto(id=2, nombre="Leche", precio=1500, stock=0),
    Producto(id=3, nombre="Arroz", precio=2000, stock=25),
    Producto(id=4, nombre="Yerba", precio=4500, stock=3)
]

#Endpoints
@app.get("/productos")
def obtener_productos():
    return productos

@app.get("/alertas/stock")
def obtener_alertas_stock():
    alertas = []
    for producto in productos:
        estado = revisar_stock(producto)
        if estado != "STOCK NORMAL":
            alertas.append({
                "id": producto.id,
                "nombre": producto.nombre,
                "stock": producto.stock,
                "estado": estado
            })
    return alertas

@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    for producto in productos:
        if producto.id == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.post("/productos")
def crear_producto(producto: Producto):
    for producto_existente in productos:
        if producto_existente.id == producto.id:
            raise HTTPException(status_code=409, detail="Ya existe un producto con ese ID")
    productos.append(producto)
    return producto

@app.patch("/productos/{producto_id}")
def actualizar_producto(producto_id: int, cambios: ActualizacionProducto):
    for producto in productos:
        if producto.id == producto_id:
            if cambios.nombre is not None:
                producto.nombre = cambios.nombre
            if cambios.precio is not None:
                producto.precio = cambios.precio
            if cambios.stock is not None:
                producto.stock = cambios.stock
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    for producto in productos:
        if producto.id == producto_id:
            productos.remove(producto)
            return {"mensaje": "Producto eliminado correctamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")
