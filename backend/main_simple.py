from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

app = FastAPI(title="Sales Backend API", version="1.0.0")

# Add CORS middleware for React frontend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory data store (for testing)
users_db = [
    {"id": 1, "email": "admin@sales.com", "password": "admin123", "nombre": "Administrador", "activo": True},
    {"id": 2, "email": "vendedor@sales.com", "password": "venta123", "nombre": "Vendedor", "activo": True}
]

sales_db = [
    {"id": 1, "cliente_id": 1, "producto": "Laptop", "cantidad": 1, "precio": 1500.00, "descuento": 0.0, "total": 1500.00, "fecha": "2024-08-11T10:00:00", "estado": "completada"},
    {"id": 2, "cliente_id": 2, "producto": "Mouse", "cantidad": 2, "precio": 25.00, "descuento": 5.0, "total": 45.00, "fecha": "2024-08-11T11:00:00", "estado": "pendiente"}
]

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    nombre: str
    activo: bool

class VentaCreate(BaseModel):
    cliente_id: int
    producto: str
    cantidad: int
    precio: float
    descuento: float = 0.0

class Venta(BaseModel):
    id: int
    cliente_id: int
    producto: str
    cantidad: int
    precio: float
    descuento: float
    total: float
    fecha: str
    estado: str

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Sales Backend API v1.0", 
        "status": "funcionando",
        "docs": "/docs"
    }

# Authentication endpoint
@app.post("/token", response_model=Token)
def login(user_data: UserLogin):
    """Simple login endpoint"""
    # Find user in our simple database
    user = next((u for u in users_db if u["email"] == user_data.username and u["password"] == user_data.password), None)
    
    if not user or not user["activo"]:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Return a simple token (not JWT for simplicity)
    return {"access_token": f"simple_token_{user['id']}", "token_type": "bearer"}

# Sales endpoints
@app.get("/ventas")
def get_ventas():
    """Get all sales"""
    return sales_db

@app.post("/ventas", response_model=Venta)
def create_venta(venta: VentaCreate):
    """Create new sale"""
    # Calculate total
    subtotal = venta.cantidad * venta.precio
    total = subtotal - venta.descuento
    
    # Create new sale
    new_sale = {
        "id": len(sales_db) + 1,
        "cliente_id": venta.cliente_id,
        "producto": venta.producto,
        "cantidad": venta.cantidad,
        "precio": venta.precio,
        "descuento": venta.descuento,
        "total": total,
        "fecha": datetime.now().isoformat(),
        "estado": "pendiente"
    }
    
    sales_db.append(new_sale)
    return new_sale

@app.get("/ventas/{venta_id}")
def get_venta(venta_id: int):
    """Get specific sale"""
    venta = next((v for v in sales_db if v["id"] == venta_id), None)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

# Dashboard stats
@app.get("/dashboard/stats")
def get_dashboard_stats():
    """Dashboard statistics"""
    total_ventas = sum(v["total"] for v in sales_db)
    cantidad_ventas = len(sales_db)
    
    return {
        "ventas_mes": total_ventas,
        "cantidad_ventas": cantidad_ventas,
        "clientes_nuevos": 2,
        "meta_mes": 75
    }

# Clients endpoint
@app.get("/clientes")
def get_clientes():
    """Get clients list"""
    return [
        {"id": 1, "nombre": "María García", "email": "maria@email.com", "telefono": "+57 300 123 4567"},
        {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com", "telefono": "+57 301 234 5678"}
    ]

if __name__ == "__main__":
    import uvicorn
    print("Iniciando Sales Backend API en http://127.0.0.1:8001")
    print("Documentacion en http://127.0.0.1:8001/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)