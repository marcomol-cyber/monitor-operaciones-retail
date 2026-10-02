###Funciones###
def revisar_stock(producto):
    if producto["stock"] == 0:
        return "SIN STOCK"
    elif producto["stock"] < 5:
        return "STOCK CRÍTICO"
    else:
        return "STOCK NORMAL"
    
###Datos###
productos = [
    {"id": 1, "nombre": "Café", "precio": 8000, "stock": 7},
    {"id": 2, "nombre": "Leche", "precio": 1500, "stock": 0},
    {"id": 3, "nombre": "Arroz", "precio": 2000, "stock": 25},
    {"id": 4, "nombre": "Yerba", "precio": 4500, "stock": 3}
]

for producto in productos:
    estado = revisar_stock(producto)
    print(producto["nombre"], "-", estado)
