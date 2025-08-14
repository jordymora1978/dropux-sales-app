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
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        # Clean the URLs of any potential whitespace/newlines and fix malformed URLs
        supabase_url = supabase_url.replace('\n', '').replace(' ', '').strip()
        supabase_key = supabase_key.replace('\n', '').replace(' ', '').strip()
        
        # Ensure URL is properly formatted
        if not supabase_url.startswith('https://'):
            supabase_url = 'https://' + supabase_url.replace('https://', '')
        
        supabase = create_client(supabase_url, supabase_key)
        print(f"✅ Supabase connected successfully to {supabase_url}")
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
app_env = os.getenv("APP_ENV", "development")
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
            "SUPABASE_URL": os.getenv("SUPABASE_URL") is not None,
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY") is not None,
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
def test_database():
    """Test Supabase connection and diagnose table access issues"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        # Debug the Supabase client configuration
        raw_url = os.getenv("SUPABASE_URL", "NOT_SET")
        cleaned_url = supabase.supabase_url if supabase else "NOT_CONNECTED"
        
        debug_info = {
            "raw_env_url": repr(raw_url),
            "cleaned_url": cleaned_url,
            "url_length": len(cleaned_url) if isinstance(cleaned_url, str) else 0,
            "url_fixed": raw_url != cleaned_url if raw_url != "NOT_SET" else False,
        }
        
        # Now that URL is fixed, get comprehensive database info
        tables_info = {}
        table_names = ['users', 'ml_stores', 'orders', 'products', 'ml_accounts']
        
        for table_name in table_names:
            try:
                # Get count and sample data
                response = supabase.table(table_name).select("*").execute()
                if response.data:
                    tables_info[table_name] = {
                        "exists": True,
                        "count": len(response.data),
                        "columns": list(response.data[0].keys()) if response.data else [],
                        "sample_record": response.data[0] if response.data else None
                    }
                else:
                    tables_info[table_name] = {
                        "exists": True,
                        "count": 0,
                        "columns": [],
                        "sample_record": None
                    }
            except Exception as e:
                tables_info[table_name] = {
                    "exists": False,
                    "error": str(e)[:100]
                }
        
        # Get total user count as mentioned by user (expected 3)
        try:
            all_users = supabase.table('users').select("*").execute()
            total_users = len(all_users.data) if all_users.data else 0
            users_preview = all_users.data[:3] if all_users.data else []
        except Exception as e:
            total_users = f"Error: {str(e)[:50]}"
            users_preview = []
        
        return {
            "status": "connected", 
            "database": "Supabase",
            "project_id": "qzexuqkedukcwcyhrpza",
            "total_users": total_users,
            "users_preview": users_preview,
            "tables": tables_info,
            "debug_info": debug_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:200],
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Iniciando DROPUX API en http://{host}:{port}")
    print(f"Documentacion en http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)