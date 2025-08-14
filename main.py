from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="DROPUX API", 
    version="2.0.0",
    description="Modern Dropshipping Platform - Amazon to MercadoLibre",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - production ready
cors_origins = ["*"] if os.getenv("APP_ENV") != "production" else [
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
@app.get("/status")
def system_status():
    """System status and configuration info"""
    return {
        "api": "DROPUX",
        "version": "2.0.0",
        "status": "operational",
        "environment": os.getenv("APP_ENV", "development"),
        "timestamp": datetime.now().isoformat(),
        "features": {
            "authentication": False,  # Will be True when JWT is added
            "database": False,        # Will be True when Supabase is connected
            "mercadolibre": False,    # Will be True when ML OAuth is added
            "cors_enabled": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Iniciando DROPUX API en http://{host}:{port}")
    print(f"Documentacion en http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)