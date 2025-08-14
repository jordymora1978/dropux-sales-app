from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import hashlib

# Importar modelos y base de datos
from models.database import get_db
from models.tables import User, Company, Venta, Cliente

load_dotenv()

app = FastAPI(title="DROPUX API", version="2.0.0")

# 🚨 CONFIGURACIÓN CORS CRÍTICA para React (CORREGIDO para puerto 3001)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = "tu_clave_secreta_super_segura_aqui_12345"
ALGORITHM = "HS256"
security = HTTPBearer()

# ==================== MODELOS PYDANTIC ====================
class UserLogin(BaseModel):
    username: str  # Cambiado para compatibilidad con frontend
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    active: bool
    company_id: int

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
    fecha: datetime
    estado: str

# ==================== JWT FUNCTIONS ====================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)  # Token válido por 24 horas
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================
@app.get("/")
def read_root():
    return {
        "message": "DROPUX API v2.0", 
        "status": "funcionando",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "DROPUX API"}

def hash_password(password: str) -> str:
    """Hash password usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/token", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Endpoint de login compatible con frontend React"""
    try:
        # Buscar usuario en base de datos con SQLAlchemy
        user = db.query(User).filter(User.email == user_data.username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        # Verificar contraseña con hash
        if user.password_hash != hash_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        # Incluir role y company_id en el token
        access_token = create_access_token(data={
            "sub": user.email,
            "role": user.role,
            "company_id": user.company_id
        })
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/profile", response_model=UserResponse)
async def get_profile(current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Obtener perfil del usuario autenticado"""
    try:
        user = db.query(User).filter(User.email == current_user).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            active=user.active,
            company_id=user.company_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==================== ENDPOINTS DE VENTAS ====================
@app.get("/ventas")
async def get_ventas(current_user: str = Depends(verify_token)):
    """Obtener todas las ventas"""
    try:
        result = supabase.table('ventas').select('*').order('fecha', desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")

@app.post("/ventas", response_model=Venta)
async def create_venta(venta: VentaCreate, current_user: str = Depends(verify_token)):
    """Crear nueva venta"""
    try:
        # Calcular total
        subtotal = venta.cantidad * venta.precio
        total = subtotal - venta.descuento
        
        venta_data = {
            "cliente_id": venta.cliente_id,
            "producto": venta.producto,
            "cantidad": venta.cantidad,
            "precio": venta.precio,
            "descuento": venta.descuento,
            "total": total,
            "fecha": datetime.now().isoformat(),
            "estado": "pendiente"
        }
        
        result = supabase.table('ventas').insert(venta_data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear venta: {str(e)}")

@app.get("/ventas/{venta_id}")
async def get_venta(venta_id: int, current_user: str = Depends(verify_token)):
    """Obtener venta específica"""
    try:
        result = supabase.table('ventas').select('*').eq('id', venta_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.put("/ventas/{venta_id}")
async def update_venta(venta_id: int, estado: str, current_user: str = Depends(verify_token)):
    """Actualizar estado de venta"""
    try:
        result = supabase.table('ventas').update({"estado": estado}).eq('id', venta_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==================== DASHBOARD STATS ====================
@app.get("/dashboard/stats")
async def get_dashboard_stats(current_user: str = Depends(verify_token)):
    """Estadísticas para el dashboard"""
    try:
        # Ventas del mes actual
        current_month = datetime.now().strftime('%Y-%m')
        ventas_mes = supabase.table('ventas').select('total').gte('fecha', f'{current_month}-01').execute()
        
        total_ventas_mes = sum(venta['total'] for venta in ventas_mes.data) if ventas_mes.data else 0
        cantidad_ventas = len(ventas_mes.data) if ventas_mes.data else 0
        
        # Clientes únicos
        clientes_unicos = supabase.table('ventas').select('cliente_id').execute()
        clientes_count = len(set(venta['cliente_id'] for venta in clientes_unicos.data)) if clientes_unicos.data else 0
        
        return {
            "ventas_mes": total_ventas_mes,
            "cantidad_ventas": cantidad_ventas,
            "clientes_nuevos": clientes_count,
            "meta_mes": 87  # Porcentaje de meta alcanzada
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# ==================== CLIENTES ENDPOINTS ====================
@app.get("/clientes")
async def get_clientes(current_user: str = Depends(verify_token)):
    """Obtener lista de clientes"""
    # Por ahora datos de ejemplo, puedes crear tabla clientes después
    return [
        {"id": 1, "nombre": "María García", "email": "maria@email.com", "telefono": "+57 300 123 4567"},
        {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com", "telefono": "+57 301 234 5678"},
        {"id": 3, "nombre": "Ana Martínez", "email": "ana@email.com", "telefono": "+57 302 345 6789"}
    ]

# ==================== ENDPOINTS LEGACY (compatibilidad) ====================
@app.post("/login")
def login_legacy(user: UserLogin):
    """Endpoint legacy para compatibilidad"""
    return {"message": "Usar /token en su lugar", "redirect": "/token"}

@app.get("/usuarios")
def get_usuarios(current_user: str = Depends(verify_token)):
    """Obtener usuarios (requiere autenticación)"""
    try:
        response = supabase.table('usuarios').select("*").execute()
        return {"usuarios": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENDPOINTS MERCADOLIBRE ====================
@app.get("/ml/auth")
async def ml_auth():
    """Obtener URL de autorización de MercadoLibre"""
    from services.mercadolibre import MercadoLibreService
    
    ml_service = MercadoLibreService()
    auth_url = ml_service.get_auth_url("MCO")  # Colombia por defecto
    
    return {"auth_url": auth_url}

@app.get("/ml/callback")
async def ml_callback(code: str, state: str = "MCO", db: Session = Depends(get_db)):
    """Callback de autorización de MercadoLibre"""
    from services.mercadolibre import MercadoLibreService
    
    try:
        ml_service = MercadoLibreService()
        
        # Intercambiar código por tokens
        tokens = await ml_service.exchange_code_for_tokens(code)
        
        # Obtener info del usuario
        user_info = await ml_service.get_user_info(tokens["access_token"])
        
        # TODO: Guardar en base de datos
        # Crear o actualizar MLAccount
        
        return {
            "message": "Autorización exitosa",
            "user_id": user_info.get("id"),
            "nickname": user_info.get("nickname"),
            "site_id": state
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en callback ML: {str(e)}")

@app.post("/todoencargo/webhooks/ml")
async def ml_webhook(request: dict):
    """Webhook para notificaciones de MercadoLibre"""
    try:
        # TODO: Procesar diferentes tipos de notificaciones
        # - orders: Nueva orden
        # - messages: Nuevo mensaje
        # - claims: Nuevo reclamo
        
        notification_type = request.get("topic")
        resource_id = request.get("resource")
        
        print(f"Webhook ML: {notification_type} - {resource_id}")
        
        # Responder rápido a ML
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0" if os.getenv("RAILWAY_ENVIRONMENT") else "127.0.0.1"
    
    print(f"Iniciando DROPUX API en http://{host}:{port}")
    print(f"Documentacion en http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port, reload=True)