"""
MercadoLibre Connection Endpoints - Professional Implementation
Handles multi-tenant ML store connections
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, validator
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ml_oauth_service import ml_oauth_service, MLTokens
from typing import Optional, List

# Import dependencies - avoiding circular imports
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from supabase import create_client
import os

# Type hints compatible with Python 3.11+
from typing import Dict, Union, Optional

AuthData = Dict[str, Union[str, int]]
StoreData = Dict[str, Union[str, int, None]]

# Initialize dependencies locally to avoid circular import
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dropux_jwt_super_secret_key_2024_v2_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Initialize Supabase client locally
supabase = None
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        supabase_url = supabase_url.replace('\n', '').replace(' ', '').strip()
        supabase_key = supabase_key.replace('\n', '').replace(' ', '').strip()
        
        if not supabase_url.startswith('https://'):
            supabase_url = 'https://' + supabase_url.replace('https://', '')
        
        supabase = create_client(supabase_url, supabase_key)
except Exception:
    supabase = None

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthData:
    """Verify JWT token and return user data."""
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

router = APIRouter(prefix="/api/ml", tags=["MercadoLibre"])

# ==================== PYDANTIC MODELS ====================

class MLStoreConnection(BaseModel):
    """Model for connecting a new ML store."""
    site_id: str = Field(..., description="ML Site ID (MLC, MCO, MLA, etc)")
    app_id: str = Field(..., description="ML App ID from developers console")
    app_secret: str = Field(..., description="ML App Secret")
    store_name: str = Field(..., description="Friendly name for this store")
    
    @validator('site_id')
    def validate_site_id(cls, v):
        valid_sites = ['MCO', 'MLC', 'MPE']  # Colombia, Chile, Perú - Dropux focus markets
        if v not in valid_sites:
            raise ValueError(f'Invalid site_id. Must be one of: {", ".join(valid_sites)} (Colombia, Chile, Perú)')
        return v
    
    @validator('app_id')
    def validate_app_id(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('App ID must be numeric and at least 10 digits')
        return v

class MLStoreResponse(BaseModel):
    """Response after initiating ML connection."""
    store_id: int
    auth_url: str
    redirect_uri: str
    message: str
    instructions: Optional[List[str]] = None

class MLStoreInfo(BaseModel):
    """Information about a connected ML store."""
    id: int
    store_name: str
    site_id: str
    site_name: str
    nickname: Optional[str]
    is_connected: bool
    connected_at: Optional[str]
    last_refreshed: Optional[str]

# ==================== ENDPOINTS ====================

@router.get("/sites")
async def get_available_sites() -> dict:
    """Get list of available MercadoLibre sites/countries - DROPUX Focus: Colombia, Chile, Perú."""
    sites = []
    for site_id, info in ml_oauth_service.ML_SITES.items():
        sites.append({
            "site_id": site_id,
            "country": info['name'],
            "domain": f"mercadolibre.{info['domain']}",
            "flag": info['flag'],
            "currency": info.get('currency', 'USD'),
            "is_active": True,
            "order": 1 if site_id == "MCO" else 2 if site_id == "MLC" else 3  # Colombia first, then Chile, then Peru
        })
    
    # Sort by order (Colombia, Chile, Peru)
    sites.sort(key=lambda x: x['order'])
    
    return {
        "sites": sites,
        "total": len(sites),
        "focus_markets": ["Colombia", "Chile", "Perú"],
        "note": "Dropux se enfoca en los principales mercados de América Latina"
    }

@router.post("/connect-store", response_model=MLStoreResponse)
async def connect_ml_store(
    request: MLStoreConnection,
    current_user: AuthData = Depends(verify_token)
) -> MLStoreResponse:
    """
    Step 1: Register ML app credentials and generate OAuth URL.
    User will be redirected to ML to authorize the connection.
    """
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Validate credentials format
        if not ml_oauth_service.validate_credentials(request.app_id, request.app_secret):
            raise HTTPException(
                status_code=400,
                detail="Invalid app credentials format. Please check your ML Developer Console."
            )
        
        # Generate unique redirect URI for this connection
        redirect_uri = ml_oauth_service.generate_redirect_uri(
            current_user["user_id"],
            request.site_id
        )
        
        # Encrypt the app secret before storing
        encrypted_secret = ml_oauth_service.encrypt_secret(request.app_secret)
        
        # Generate state token for CSRF protection
        state = ml_oauth_service.generate_state_token(current_user["user_id"])
        
        # Store initial connection data
        store_data = {
            "user_id": current_user["user_id"],
            "company_id": current_user["company_id"],
            "site_id": request.site_id,
            "nickname": request.store_name,
            "app_id": request.app_id,
            "app_secret_encrypted": encrypted_secret,
            "redirect_uri": redirect_uri,
            "state_token": state,
            "status": "pending_authorization",
            "created_at": datetime.now().isoformat()
        }
        
        # Check if store already exists for this user
        existing = supabase.table('ml_accounts').select("*").eq(
            'user_id', current_user["user_id"]
        ).eq('site_id', request.site_id).eq('app_id', request.app_id).execute()
        
        if existing.data:
            # Update existing store
            response = supabase.table('ml_accounts').update(store_data).eq(
                'id', existing.data[0]['id']
            ).execute()
            store_id = existing.data[0]['id']
        else:
            # Create new store
            response = supabase.table('ml_accounts').insert(store_data).execute()
            store_id = response.data[0]['id'] if response.data else None
        
        if not store_id:
            raise HTTPException(status_code=500, detail="Failed to save store configuration")
        
        # Generate OAuth URL
        auth_url = ml_oauth_service.get_auth_url(
            site_id=request.site_id,
            client_id=request.app_id,
            redirect_uri=redirect_uri,
            state=state
        )
        
        # Prepare instructions for the user
        instructions = [
            f"1. Copy this Redirect URI: {redirect_uri}",
            "2. Go to your ML App in developers console",
            "3. Paste the Redirect URI in the 'Redirect URI' field",
            "4. Save your ML App settings",
            "5. Click the 'Connect Now' button below to authorize"
        ]
        
        return MLStoreResponse(
            store_id=store_id,
            auth_url=auth_url,
            redirect_uri=redirect_uri,
            message=f"Store '{request.store_name}' configured. Follow the instructions to complete connection.",
            instructions=instructions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")

@router.get("/callback/{callback_id}")
async def ml_oauth_callback(
    callback_id: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None
) -> dict:
    """
    Step 2: Handle OAuth callback from MercadoLibre.
    Exchange authorization code for access tokens.
    """
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Handle ML authorization errors
    if error:
        return {
            "status": "error",
            "message": f"MercadoLibre authorization failed: {error_description or error}"
        }
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing authorization code or state")
    
    try:
        # Find the store by state token
        store_response = supabase.table('ml_accounts').select("*").eq(
            'state_token', state
        ).eq('status', 'pending_authorization').execute()
        
        if not store_response.data:
            raise HTTPException(status_code=404, detail="Invalid or expired authorization request")
        
        store = store_response.data[0]
        
        # Validate state token for CSRF protection
        if not ml_oauth_service.validate_state_token(state, store['user_id']):
            raise HTTPException(status_code=403, detail="Invalid state token")
        
        # Decrypt app secret
        app_secret = ml_oauth_service.decrypt_secret(store['app_secret_encrypted'])
        
        # Exchange code for tokens
        tokens = await ml_oauth_service.exchange_code_for_tokens(
            code=code,
            client_id=store['app_id'],
            client_secret=app_secret,
            redirect_uri=store['redirect_uri'],
            site_id=store['site_id']
        )
        
        # Get ML user info
        user_info = await ml_oauth_service.get_user_info(tokens['access_token'])
        
        # Update store with tokens and user info
        update_data = {
            "access_token": tokens['access_token'],
            "refresh_token": tokens['refresh_token'],
            "ml_user_id": user_info['id'],
            "nickname": user_info.get('nickname', store['nickname']),
            "status": "connected",
            "connected_at": datetime.now().isoformat(),
            "token_expires_at": datetime.fromtimestamp(
                datetime.now().timestamp() + tokens.get('expires_in', 21600)
            ).isoformat()
        }
        
        supabase.table('ml_accounts').update(update_data).eq('id', store['id']).execute()
        
        # Return success with redirect to dashboard
        return {
            "status": "success",
            "message": f"Store '{store['nickname']}' connected successfully!",
            "store_id": store['id'],
            "ml_user": user_info.get('nickname'),
            "redirect_url": f"{os.getenv('FRONTEND_URL', 'https://sales.dropux.co')}/dashboard?connection=success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback error: {str(e)}")

@router.get("/my-stores", response_model=List[MLStoreInfo])
async def get_my_stores(
    current_user: AuthData = Depends(verify_token)
) -> List[MLStoreInfo]:
    """Get all ML stores connected by the current user."""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        response = supabase.table('ml_accounts').select("*").eq(
            'user_id', current_user["user_id"]
        ).execute()
        
        stores = []
        for store in response.data or []:
            site_info = ml_oauth_service.ML_SITES.get(store['site_id'], {})
            
            stores.append(MLStoreInfo(
                id=store['id'],
                store_name=store.get('nickname', 'Unknown Store'),
                site_id=store['site_id'],
                site_name=site_info.get('name', store['site_id']),
                nickname=store.get('ml_nickname'),
                is_connected=store.get('status') == 'connected',
                connected_at=store.get('connected_at'),
                last_refreshed=store.get('token_refreshed_at')
            ))
        
        return stores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stores: {str(e)}")

@router.post("/refresh-token/{store_id}")
async def refresh_store_token(
    store_id: int,
    current_user: AuthData = Depends(verify_token)
) -> dict:
    """Manually refresh access token for a specific store."""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get store and verify ownership
        store_response = supabase.table('ml_accounts').select("*").eq(
            'id', store_id
        ).eq('user_id', current_user["user_id"]).execute()
        
        if not store_response.data:
            raise HTTPException(status_code=404, detail="Store not found")
        
        store = store_response.data[0]
        
        if not store.get('refresh_token'):
            raise HTTPException(status_code=400, detail="Store not connected or missing refresh token")
        
        # Decrypt app secret
        app_secret = ml_oauth_service.decrypt_secret(store['app_secret_encrypted'])
        
        # Refresh the token
        new_tokens = await ml_oauth_service.refresh_access_token(
            refresh_token=store['refresh_token'],
            client_id=store['app_id'],
            client_secret=app_secret,
            site_id=store['site_id']
        )
        
        # Update store with new tokens
        update_data = {
            "access_token": new_tokens['access_token'],
            "refresh_token": new_tokens.get('refresh_token', store['refresh_token']),
            "token_refreshed_at": datetime.now().isoformat(),
            "token_expires_at": datetime.fromtimestamp(
                datetime.now().timestamp() + new_tokens.get('expires_in', 21600)
            ).isoformat()
        }
        
        supabase.table('ml_accounts').update(update_data).eq('id', store_id).execute()
        
        return {
            "status": "success",
            "message": "Token refreshed successfully",
            "expires_in": new_tokens.get('expires_in', 21600)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh error: {str(e)}")

@router.delete("/disconnect/{store_id}")
async def disconnect_store(
    store_id: int,
    current_user: AuthData = Depends(verify_token)
) -> dict:
    """Disconnect a ML store (removes tokens but keeps configuration)."""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Verify ownership
        store_response = supabase.table('ml_accounts').select("*").eq(
            'id', store_id
        ).eq('user_id', current_user["user_id"]).execute()
        
        if not store_response.data:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Clear sensitive data but keep configuration
        update_data = {
            "access_token": None,
            "refresh_token": None,
            "status": "disconnected",
            "disconnected_at": datetime.now().isoformat()
        }
        
        supabase.table('ml_accounts').update(update_data).eq('id', store_id).execute()
        
        return {
            "status": "success",
            "message": "Store disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disconnect error: {str(e)}")