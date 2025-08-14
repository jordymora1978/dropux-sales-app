from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Optional[Client] = None
try:
    # TEMPORARY: Hardcoded while Railway variables issue is resolved
    supabase_url = os.getenv("SUPABASE_URL") or "https://qzexuqkedukcwcyhrpza.supabase.co"
    supabase_key = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6ZXh1cWtlZHVrY3djeWhycHphIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3NDEzODcsImV4cCI6MjA2OTMxNzM4N30.T_lXTVGZCFGA5rjVWQNo3WphIE2YPaifxonHIGPMkI0"
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase connected successfully")
    else:
        print("⚠️ Supabase credentials not found")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")
    supabase = None

app = FastAPI(
    title="DROPUX API", 
    version="2.0.0",
    description="Modern Dropshipping Platform - Amazon to MercadoLibre",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - production ready
# TEMPORARY: Hardcoded while Railway variables issue is resolved
app_env = os.getenv("APP_ENV") or "production"
cors_origins = ["*"] if app_env != "production" else [
    "https://dropux.co",
    "https://sales.dropux.co",
    "https://www.dropux.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================
class APIInfo(BaseModel):
    message: str
    status: str
    docs: str
    version: str
    environment: str

class HealthCheck(BaseModel):
    status: str
    service: str
    timestamp: str
    environment: str

@app.get("/", response_model=APIInfo)
def read_root():
    """
    API Information endpoint
    Returns basic information about the DROPUX API
    """
    return APIInfo(
        message="DROPUX API v2.0",
        status="funcionando", 
        docs="/docs",
        version="2.0.0",
        environment=os.getenv("APP_ENV", "development")
    )

@app.get("/health", response_model=HealthCheck)
def health_check():
    """
    Health Check endpoint for monitoring
    Used by Railway and other monitoring services
    """
    return HealthCheck(
        status="healthy",
        service="DROPUX API",
        timestamp=datetime.now().isoformat(),
        environment=os.getenv("APP_ENV", "development")
    )

@app.get("/test")
def test_endpoint():
    """Test endpoint for development purposes"""
    return {
        "message": "Test successful", 
        "environment": os.getenv("APP_ENV", "development"),
        "timestamp": datetime.now().isoformat(),
        "cors_origins": cors_origins
    }

# ==================== UTILITY ENDPOINTS ====================
@app.get("/env-check")
def environment_check():
    """Check which environment variables are set (for debugging)"""
    return {
        "environment": os.getenv("APP_ENV", "NOT_SET"),
        "variables_detected": {
            "APP_ENV": os.getenv("APP_ENV") is not None,
            "DEBUG": os.getenv("DEBUG") is not None,
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY") is not None,
            "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM") is not None,
            "ML_CLIENT_ID": os.getenv("ML_CLIENT_ID") is not None,
            "ML_CLIENT_SECRET": os.getenv("ML_CLIENT_SECRET") is not None,
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT") is not None,
            "PORT": os.getenv("PORT") is not None
        },
        "railway_provided": {
            "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
            "RAILWAY_PROJECT_ID": os.getenv("RAILWAY_PROJECT_ID"),
            "RAILWAY_SERVICE_NAME": os.getenv("RAILWAY_SERVICE_NAME")
        }
    }

@app.get("/status")
def system_status():
    """System status and configuration info"""
    return {
        "api": "DROPUX",
        "version": "2.0.0",
        "status": "operational",
        "environment": app_env,
        "timestamp": datetime.now().isoformat(),
        "features": {
            "authentication": bool(os.getenv("JWT_SECRET_KEY")),
            "database": supabase is not None,
            "mercadolibre": False,  # Now multi-tenant, no global ML vars
            "cors_enabled": True
        },
        "debug_info": {
            "app_env": os.getenv("APP_ENV"),
            "has_jwt_key": bool(os.getenv("JWT_SECRET_KEY")),
            "supabase_connected": supabase is not None,
            "is_railway": bool(os.getenv("RAILWAY_ENVIRONMENT")),
            "port": os.getenv("PORT")
        }
    }

@app.get("/db-test")
async def test_database():
    """Test Supabase connection and list tables"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        # Try to query a simple table or get table info
        # This will verify the connection works
        response = supabase.table('users').select("count", count='exact').execute()
        
        return {
            "status": "connected",
            "database": "Supabase",
            "project_id": "qzexuqkedukcwcyhrpza",
            "users_count": response.count if hasattr(response, 'count') else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Iniciando DROPUX API en http://{host}:{port}")
    print(f"Documentacion en http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)