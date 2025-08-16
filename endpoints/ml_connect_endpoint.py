from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import secrets
import hashlib
from datetime import datetime

router = APIRouter(prefix="/api/ml", tags=["MercadoLibre"])

# ==================== MODELS ====================
class MLStoreConnect(BaseModel):
    """Model for connecting a new ML store"""
    site_id: str  # MLC, MCO, MLA, etc.
    app_number: str
    app_id: str  # Client ID
    app_secret: str  # Client Secret
    store_name: Optional[str] = None

class MLStoreResponse(BaseModel):
    """Response after setting up ML store"""
    id: str
    store_name: str
    site_id: str
    redirect_uri: str
    auth_url: str
    is_connected: bool

# ==================== ENDPOINTS ====================

@router.post("/stores/setup", response_model=MLStoreResponse)
async def setup_ml_store(
    store_data: MLStoreConnect,
    current_user = Depends(get_current_user)  # JWT auth
):
    """
    Step 1: User registers their ML app credentials
    This happens BEFORE OAuth connection
    """
    
    # Generate unique redirect URI for this store
    unique_hash = hashlib.md5(f"{current_user.id}{store_data.app_id}".encode()).hexdigest()[:16]
    redirect_uri = f"https://sales.dropux.co/api/ml/callback/{unique_hash}"
    
    # Save to database
    store = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "store_name": store_data.store_name or f"Tienda {store_data.site_id}",
        "site_id": store_data.site_id,
        "app_number": store_data.app_number,
        "app_id": store_data.app_id,
        "app_secret": encrypt(store_data.app_secret),  # Encrypt before saving
        "redirect_uri": redirect_uri,
        "is_connected": False,
        "created_at": datetime.now()
    }
    
    # TODO: Save to Supabase
    # await supabase.table('ml_stores').insert(store).execute()
    
    # Generate OAuth URL for MercadoLibre
    ml_sites = {
        "MLA": "https://auth.mercadolibre.com.ar",
        "MLB": "https://auth.mercadolibre.com.br", 
        "MCO": "https://auth.mercadolibre.com.co",
        "MCR": "https://auth.mercadolibre.com.cr",
        "MEC": "https://auth.mercadolibre.com.ec",
        "MLC": "https://auth.mercadolibre.cl",
        "MLM": "https://auth.mercadolibre.com.mx",
        "MLU": "https://auth.mercadolibre.com.uy",
        "MLA": "https://auth.mercadolibre.com.ar",
        "MPE": "https://auth.mercadolibre.com.pe",
        "MLV": "https://auth.mercadolibre.com.ve",
        "MPA": "https://auth.mercadolibre.com.pa",
        "MPY": "https://auth.mercadolibre.com.py",
        "MBO": "https://auth.mercadolibre.com.bo"
    }
    
    auth_base_url = ml_sites.get(store_data.site_id, "https://auth.mercadolibre.com")
    
    # Create state token for security
    state_token = secrets.token_urlsafe(32)
    # TODO: Save state_token in Redis/cache with store_id
    
    auth_url = f"{auth_base_url}/authorization?response_type=code&client_id={store_data.app_id}&redirect_uri={redirect_uri}&state={state_token}"
    
    return MLStoreResponse(
        id=store["id"],
        store_name=store["store_name"],
        site_id=store["site_id"],
        redirect_uri=redirect_uri,
        auth_url=auth_url,
        is_connected=False
    )

@router.get("/stores")
async def get_user_stores(
    current_user = Depends(get_current_user)
):
    """
    Get all ML stores for current user
    """
    # TODO: Query from Supabase
    # stores = await supabase.table('ml_stores').select('*').eq('user_id', current_user.id).execute()
    
    stores = []  # Placeholder
    
    return {
        "stores": stores,
        "total": len(stores)
    }

@router.get("/callback/{store_hash}")
async def ml_oauth_callback(
    store_hash: str,
    code: str,
    state: str
):
    """
    Step 2: ML redirects here after user authorizes
    Exchange code for tokens and complete connection
    """
    
    # TODO: Validate state token from cache
    # TODO: Find store by redirect_uri hash
    # TODO: Exchange code for tokens
    # TODO: Get ML user info
    # TODO: Update store with tokens and ML info
    # TODO: Mark as connected
    
    # Redirect to frontend success page
    return RedirectResponse(url=f"https://dropux.co/dashboard/stores?connected=true")

@router.post("/stores/{store_id}/disconnect")
async def disconnect_store(
    store_id: str,
    current_user = Depends(get_current_user)
):
    """
    Disconnect a ML store (revoke tokens)
    """
    # TODO: Verify store belongs to user
    # TODO: Revoke tokens with ML API
    # TODO: Clear tokens from database
    
    return {"message": "Store disconnected successfully"}

@router.post("/stores/{store_id}/refresh")
async def refresh_store_token(
    store_id: str,
    current_user = Depends(get_current_user)
):
    """
    Refresh access token using refresh token
    """
    # TODO: Get store from database
    # TODO: Use refresh_token to get new access_token
    # TODO: Update database with new tokens
    
    return {"message": "Token refreshed successfully"}