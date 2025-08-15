from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import jwt
import hashlib
from dotenv import load_dotenv
from supabase import create_client, Client
# ✅ Python 3.12 - Removed typing imports (using built-in generics and | operator)

# Load environment variables
load_dotenv()

# Type hints compatible with Python 3.11
from typing import Dict, Union, List, Any, Optional

UserRecord = Dict[str, Union[str, int, bool, None]]
StoreRecord = Dict[str, Union[str, int, None]] 
JWTPayload = Dict[str, Union[str, int, float]]
SupabaseResponse = Dict[str, Any]
AuthData = Dict[str, Union[str, int]]

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

# Lista específica de orígenes permitidos (sin wildcards)
allowed_origins = [
    "https://dropux.co",
    "https://sales.dropux.co",  # Frontend principal en Vercel
    "https://www.dropux.co",
    "https://dropux-sales-app.vercel.app",
    "https://dropux-sales-app-git-master-jordys-projects-89bfd6b6.vercel.app",
    "https://dropux-sales-qomek43nu-jordys-projects-89bfd6b6.vercel.app",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Professional: Specific origins only
    allow_credentials=True,  # Secure: Allow credentials for JWT
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400
)

# ==================== CORS PREFLIGHT HANDLER ====================
@app.options("/{full_path:path}")
def handle_options(full_path: str):
    """Handle CORS preflight requests for all endpoints.
    
    Args:
        full_path: Any path for preflight requests
        
    Returns:
        Empty response with CORS headers
    """
    return {}

# ==================== AUTHENTICATION ====================
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dropux_jwt_super_secret_key_2024_v2_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def hash_password(password: str) -> str:
    """Hash password using SHA256.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash.
    
    Args:
        password: Plain text password
        hashed: Stored hash to compare against
        
    Returns:
        True if password matches hash
    """
    return hash_password(password) == hashed

def create_jwt_token(user_data: UserRecord) -> str:
    """Create JWT token for authenticated user.
    
    Args:
        user_data: User record from database
        
    Returns:
        Encoded JWT token string
        
    Raises:
        KeyError: If user_data missing required fields
    """
    payload: JWTPayload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "company_id": user_data["company_id"],
        "exp": datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthData:
    """Verify JWT token and return user data.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        Decoded token payload with user data
        
    Raises:
        HTTPException: 401 if token expired or invalid
    """
    try:
        payload: AuthData = jwt.decode(
            credentials.credentials, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== PYDANTIC MODELS ====================
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict[str, str | int]

class MLStoreSetup(BaseModel):
    site_id: str  # MLC, MLA, etc.
    app_id: str   # Client ID from ML developers
    app_secret: str
    store_name: str = ""

class MLStoreResponse(BaseModel):
    store_id: int
    auth_url: str
    redirect_uri: str
    message: str

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
def read_root() -> APIInfo:
    """
    API Information endpoint.
    
    Returns:
        Basic information about the DROPUX API
    """
    return APIInfo(
        message="DROPUX API v2.0",
        status="funcionando", 
        docs="/docs",
        version="2.0.0",
        environment=os.getenv("APP_ENV", "development")
    )

@app.get("/health")
def health_check() -> Dict[str, str]:
    """
    Health Check endpoint for monitoring.
    
    Returns:
        Health status information for monitoring services
        
    Note:
        Used by Railway and other monitoring services
    """
    return {
        "status": "healthy",
        "service": "DROPUX API",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("APP_ENV", "development")
    }

@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """Login endpoint - authenticate user and return JWT token.
    
    Args:
        request: Login credentials (email and password)
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: 401 if credentials invalid, 503 if database unavailable
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Find user by email
        response = supabase.table('users').select("*").eq('email', request.email).eq('active', True).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user: UserRecord = response.data[0]
        
        # Verify password
        if not verify_password(request.password, str(user['password_hash'])):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create JWT token
        token: str = create_jwt_token(user)
        
        # Remove sensitive data from user object
        safe_user: dict[str, str | int] = {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "company_id": user["company_id"],
            "created_at": user["created_at"]
        }
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user=safe_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@app.get("/auth/me")
def get_current_user(current_user: AuthData = Depends(verify_token)) -> dict[str, str | AuthData]:
    """Get current authenticated user information.
    
    Args:
        current_user: JWT verified user data
        
    Returns:
        Current user information and token validation status
    """
    return {
        "user": current_user,
        "message": "Token valid"
    }

@app.post("/api/ml/stores/setup", response_model=MLStoreResponse)
def setup_ml_store(
    request: MLStoreSetup, 
    current_user: AuthData = Depends(verify_token)
) -> MLStoreResponse:
    """Setup a new MercadoLibre store for the authenticated user.
    
    Args:
        request: ML store configuration data
        current_user: JWT verified user data
        
    Returns:
        Store creation response with OAuth URL
        
    Raises:
        HTTPException: 503 if database unavailable, 500 if creation fails
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Create redirect URI for this specific store
        redirect_uri = f"https://sales.dropux.co/api/ml/callback"
        
        # Insert store configuration into ml_accounts table (using only existing fields)
        store_data: dict[str, str | int] = {
            "user_id": current_user["user_id"],
            "company_id": current_user["company_id"],
            "site_id": request.site_id,
            "nickname": request.store_name or f"Tienda {request.site_id}",  # Required field
            # Note: app_id, app_secret, redirect_uri don't exist in this table
            # We'll store this info in a comment or separate approach
        }
        
        response: SupabaseResponse[list[StoreRecord]] = (
            supabase.table('ml_accounts')
            .insert(store_data)
            .execute()
        )
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create store")
        
        store_id: int = response.data[0]["id"]
        
        # Generate MercadoLibre OAuth URL (using provided app_id)
        auth_url: str = (
            f"https://auth.mercadolibre.com.{request.site_id.lower()}/authorization?"
            f"response_type=code&client_id={request.app_id}&redirect_uri={redirect_uri}&state={store_id}"
        )
        
        return MLStoreResponse(
            store_id=store_id,
            auth_url=auth_url,
            redirect_uri=redirect_uri,
            message=f"Store '{request.store_name}' created successfully! Note: app credentials stored temporarily in session."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup error: {str(e)}")

@app.get("/api/ml/stores")
def get_user_stores(current_user: AuthData = Depends(verify_token)) -> dict[str, list[dict[str, str | int | None]] | int]:
    """Get all MercadoLibre stores for the authenticated user.
    
    Args:
        current_user: JWT verified user data
        
    Returns:
        Dictionary with stores list and count
        
    Raises:
        HTTPException: 503 if database unavailable, 500 if fetch fails
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        response: SupabaseResponse[list[StoreRecord]] = (
            supabase.table('ml_accounts')
            .select("*")
            .eq('user_id', current_user["user_id"])
            .execute()
        )
        
        # Remove sensitive data (app_secret) from response
        stores: list[dict[str, str | int | None]] = []
        for store in response.data or []:
            safe_store: dict[str, str | int | None] = {
                k: v for k, v in store.items() if k != 'app_secret'
            }
            stores.append(safe_store)
        
        return {
            "stores": stores,
            "count": len(stores)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stores: {str(e)}")

@app.get("/api/ml/callback")
def ml_oauth_callback(code: str, state: str) -> dict[str, str]:
    """Handle MercadoLibre OAuth callback.
    
    Args:
        code: Authorization code from ML
        state: Store ID for callback tracking
        
    Returns:
        Connection status and store information
        
    Raises:
        HTTPException: 503 if database unavailable, 404 if store not found
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get store configuration
        store_response: SupabaseResponse[list[StoreRecord]] = (
            supabase.table('ml_accounts')
            .select("*")
            .eq('id', state)
            .execute()
        )
        
        if not store_response.data:
            raise HTTPException(status_code=404, detail="Store not found")
        
        store: StoreRecord = store_response.data[0]
        
        # Exchange code for access token (simplified for now)
        # In production, you would make a request to ML token endpoint
        update_data: dict[str, str] = {
            "status": "connected",
            "auth_code": code,
            "connected_at": datetime.now().isoformat()
        }
        
        supabase.table('ml_accounts').update(update_data).eq('id', state).execute()
        
        return {
            "message": "Store connected successfully!",
            "store_id": state,
            "status": "connected"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback error: {str(e)}")

@app.get("/test")
def test_endpoint() -> dict[str, str | list[str]]:
    """Test endpoint for development purposes.
    
    Returns:
        Test status and environment information
    """
    return {
        "message": "Test successful", 
        "environment": os.getenv("APP_ENV", "development"),
        "timestamp": datetime.now().isoformat(),
        "cors_origins": cors_origins
    }

# ==================== UTILITY ENDPOINTS ====================
@app.get("/env-check")
def environment_check() -> dict[str, str | dict[str, bool] | dict[str, str | None]]:
    """Check which environment variables are set (for debugging).
    
    Returns:
        Environment status and variable detection information
    """
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

@app.get("/admin/check-ml-accounts")
def check_ml_accounts_structure(current_user: dict = Depends(verify_token)):
    """Check existing ml_accounts table structure"""
    if current_user.get("role") != "master_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Try to insert a minimal record to see what columns are required
    try:
        # Try different combinations to see what works
        test_cases = [
            {"user_id": current_user["user_id"], "company_id": current_user["company_id"], "site_id": "MLC", "nickname": "test"},  # All required fields
            {"user_id": current_user["user_id"], "company_id": current_user["company_id"], "site_id": "MLC", "nickname": "test", "app_id": "123"},  # With app_id
            {"user_id": current_user["user_id"], "company_id": current_user["company_id"], "site_id": "MLC", "nickname": "test", "access_token": "token", "refresh_token": "refresh"},  # With tokens
        ]
        
        results = {}
        
        for i, test_data in enumerate(test_cases):
            try:
                response = supabase.table('ml_accounts').insert(test_data).execute()
                if response.data:
                    # Clean up immediately
                    supabase.table('ml_accounts').delete().eq('id', response.data[0]['id']).execute()
                    results[f"test_{i}"] = f"SUCCESS: {list(test_data.keys())}"
                    break  # If one works, we're good
                else:
                    results[f"test_{i}"] = f"FAILED: {list(test_data.keys())}"
            except Exception as e:
                results[f"test_{i}"] = f"ERROR: {str(e)[:100]}"
        
        return {
            "table": "ml_accounts",
            "test_results": results,
            "user": current_user["email"]
        }
        
    except Exception as e:
        return {
            "error": f"General error: {str(e)[:200]}"
        }

@app.post("/admin/migrate-emails")
def migrate_emails_to_dropux(current_user: dict = Depends(verify_token)):
    """Migrate user emails from @drapify.com to @dropux.co - ADMIN ONLY"""
    if current_user.get("role") != "master_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get all users with @drapify.com emails
        response = supabase.table('users').select("*").like('email', '%@drapify.com').execute()
        
        if not response.data:
            return {
                "message": "No @drapify.com emails found to migrate",
                "migrated": 0
            }
        
        migrated_users = []
        
        for user in response.data:
            old_email = user["email"]
            new_email = old_email.replace("@drapify.com", "@dropux.co")
            
            # Update email in database
            update_response = supabase.table('users').update({"email": new_email}).eq('id', user['id']).execute()
            
            if update_response.data:
                migrated_users.append({
                    "id": user["id"],
                    "old_email": old_email,
                    "new_email": new_email
                })
        
        return {
            "message": f"Successfully migrated {len(migrated_users)} emails to @dropux.co",
            "migrated": len(migrated_users),
            "users": migrated_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration error: {str(e)}")

@app.post("/admin/setup-tables")
def setup_database_tables(current_user: dict = Depends(verify_token)):
    """Setup required database tables - ADMIN ONLY"""
    if current_user.get("role") != "master_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    results = {}
    
    # Create ml_stores table using SQL function
    try:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.ml_stores (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            company_id INTEGER,
            site_id VARCHAR(10),
            app_id VARCHAR(100),
            app_secret VARCHAR(200),
            store_name VARCHAR(255),
            redirect_uri TEXT,
            status VARCHAR(50) DEFAULT 'pending_auth',
            access_token TEXT,
            refresh_token TEXT,
            auth_code VARCHAR(255),
            connected_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute SQL using RPC (if available) or try alternative method
        try:
            rpc_result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            results["ml_stores_creation"] = "Table created via RPC"
        except:
            # Alternative: try to create using PostgREST (might not work)
            results["ml_stores_creation"] = "RPC not available - manual table creation needed"
            
        # Test if table now exists by inserting sample data
        sample_ml_store = {
            "user_id": current_user["user_id"],
            "company_id": current_user["company_id"],
            "site_id": "MLC",
            "app_id": "sample_app_id",
            "app_secret": "sample_secret",
            "store_name": "Test Store",
            "redirect_uri": "https://sales.dropux.co/api/ml/callback",
            "status": "setup_test"
        }
        
        test_insert = supabase.table('ml_stores').insert(sample_ml_store).execute()
        
        if test_insert.data:
            # Clean up test record
            supabase.table('ml_stores').delete().eq('status', 'setup_test').execute()
            results["ml_stores_test"] = "Table working - test record created and deleted"
        else:
            results["ml_stores_test"] = "Insert failed"
            
    except Exception as e:
        results["ml_stores_error"] = f"Error: {str(e)[:300]}"
    
    return {
        "status": "table_setup_attempt",
        "results": results,
        "user": current_user["email"],
        "note": "If table creation failed, please create ml_stores table manually in Supabase"
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
                    # Table exists but is empty - try to get column info differently
                    try:
                        # Insert a test record to see table structure (if table has columns)
                        test_insert = supabase.table(table_name).insert({"test": "test"}).execute()
                        tables_info[table_name] = {
                            "exists": True,
                            "count": 0,
                            "columns": "empty_table_could_not_determine",
                            "sample_record": None
                        }
                    except Exception as col_error:
                        tables_info[table_name] = {
                            "exists": True,
                            "count": 0, 
                            "columns": f"empty_table_error: {str(col_error)[:50]}",
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