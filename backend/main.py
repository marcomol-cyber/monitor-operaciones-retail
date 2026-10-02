#Imports
from fastapi import FastAPI

#Configuración de la API
app = FastAPI(
    title="Monitor de Operaciones Retail",
    description="API para monnitorear productos, stock y operaciones retail.",
    version="0.1.0"
)

#Funciones
def revisar_stock(producto):
    if producto["stock"] == 0:
        return "SIN STOCK"
    elif producto["stock"] < 5:
        return "STOCK CRÍTICO"
    else:
        return "STOCK NORMAL"
    
#Datos
productos = [
    {"id": 1, "nombre": "Café", "precio": 8000, "stock": 7},
    {"id": 2, "nombre": "Leche", "precio": 1500, "stock": 0},
    {"id": 3, "nombre": "Arroz", "precio": 2000, "stock": 25},
    {"id": 4, "nombre": "Yerba", "precio": 4500, "stock": 3}
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
                "id": producto["id"],
                "nombre": producto["nombre"],
                "stock": producto["stock"],
                "estado": estado
            })
    return alertas