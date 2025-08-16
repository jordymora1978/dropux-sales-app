"""
MercadoLibre Orders Endpoint - Gestión de órdenes ML
Handles ML orders fetching and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.ml_oauth_service import ml_oauth_service
from typing import List, Optional, Dict, Any
import httpx
import jwt
from supabase import create_client
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Type hints compatible with Python 3.12
type AuthData = dict[str, str | int]
type OrderData = dict[str, Any]

# Initialize dependencies
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dropux_jwt_super_secret_key_2024_v2_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Initialize Supabase
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

router = APIRouter(prefix="/api/ml", tags=["MercadoLibre Orders"])

# ==================== PYDANTIC MODELS ====================

class MLOrder(BaseModel):
    """Model for ML order"""
    id: str
    status: str
    date_created: datetime
    date_closed: Optional[datetime] = None
    buyer_id: int
    buyer_nickname: str
    total_amount: float
    currency_id: str
    order_items: List[Dict[str, Any]]
    shipping: Optional[Dict[str, Any]] = None
    payments: Optional[List[Dict[str, Any]]] = None

class MLOrdersResponse(BaseModel):
    """Response for ML orders list"""
    orders: List[MLOrder]
    total: int
    offset: int
    limit: int
    store_name: str
    site_id: str

# ==================== HELPER FUNCTIONS ====================

async def get_ml_access_token(store_id: int, user_id: int) -> tuple[str, dict]:
    """Get valid access token for ML API calls, refreshing if needed."""
    
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    # Get store from database
    store_response = supabase.table('ml_accounts').select("*").eq(
        'id', store_id
    ).eq('user_id', user_id).execute()
    
    if not store_response.data:
        raise HTTPException(status_code=404, detail="Store not found")
    
    store = store_response.data[0]
    
    if store.get('status') != 'connected':
        raise HTTPException(status_code=400, detail="Store not connected")
    
    # Check if token is expired
    token_expires = store.get('token_expires_at')
    if token_expires:
        expires_dt = datetime.fromisoformat(token_expires.replace('Z', '+00:00'))
        if expires_dt < datetime.now():
            # Token expired, refresh it
            app_secret = ml_oauth_service.decrypt_secret(store['app_secret_encrypted'])
            
            new_tokens = await ml_oauth_service.refresh_access_token(
                refresh_token=store['refresh_token'],
                client_id=store['app_id'],
                client_secret=app_secret,
                site_id=store['site_id']
            )
            
            # Update tokens in database
            update_data = {
                "access_token": new_tokens['access_token'],
                "refresh_token": new_tokens.get('refresh_token', store['refresh_token']),
                "token_refreshed_at": datetime.now().isoformat(),
                "token_expires_at": datetime.fromtimestamp(
                    datetime.now().timestamp() + new_tokens.get('expires_in', 21600)
                ).isoformat()
            }
            
            supabase.table('ml_accounts').update(update_data).eq('id', store_id).execute()
            
            return new_tokens['access_token'], store
    
    return store['access_token'], store

# ==================== ENDPOINTS ====================

@router.get("/stores/{store_id}/orders", response_model=MLOrdersResponse)
async def get_ml_orders(
    store_id: int,
    current_user: AuthData = Depends(verify_token),
    offset: int = Query(0, ge=0, description="Starting position"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to fetch"),
    status: Optional[str] = Query(None, description="Filter by order status")
) -> MLOrdersResponse:
    """
    Get orders from a connected MercadoLibre store.
    Automatically refreshes token if expired.
    """
    
    try:
        # Get valid access token
        access_token, store = await get_ml_access_token(store_id, current_user["user_id"])
        
        # Build ML API URL
        ml_user_id = store.get('ml_user_id')
        if not ml_user_id:
            # Get user info first if we don't have it
            user_info = await ml_oauth_service.get_user_info(access_token)
            ml_user_id = user_info['id']
            
            # Save ML user ID for future use
            supabase.table('ml_accounts').update({
                'ml_user_id': ml_user_id,
                'ml_nickname': user_info.get('nickname')
            }).eq('id', store_id).execute()
        
        # Prepare API request
        url = f"https://api.mercadolibre.com/orders/search"
        params = {
            'seller': ml_user_id,
            'offset': offset,
            'limit': limit,
            'sort': 'date_desc'
        }
        
        if status:
            params['order.status'] = status
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Make request to ML API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code == 401:
                # Token might be invalid even if not expired, try refreshing
                app_secret = ml_oauth_service.decrypt_secret(store['app_secret_encrypted'])
                new_tokens = await ml_oauth_service.refresh_access_token(
                    refresh_token=store['refresh_token'],
                    client_id=store['app_id'],
                    client_secret=app_secret,
                    site_id=store['site_id']
                )
                
                # Update and retry
                access_token = new_tokens['access_token']
                headers['Authorization'] = f'Bearer {access_token}'
                response = await client.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else {}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ML API error: {error_detail.get('message', 'Unknown error')}"
                )
            
            data = response.json()
            
            # Parse orders
            orders = []
            for order_data in data.get('results', []):
                order = MLOrder(
                    id=order_data['id'],
                    status=order_data['status'],
                    date_created=order_data['date_created'],
                    date_closed=order_data.get('date_closed'),
                    buyer_id=order_data['buyer']['id'],
                    buyer_nickname=order_data['buyer']['nickname'],
                    total_amount=order_data['total_amount'],
                    currency_id=order_data['currency_id'],
                    order_items=order_data.get('order_items', []),
                    shipping=order_data.get('shipping'),
                    payments=order_data.get('payments')
                )
                orders.append(order)
            
            return MLOrdersResponse(
                orders=orders,
                total=data.get('paging', {}).get('total', 0),
                offset=offset,
                limit=limit,
                store_name=store.get('nickname', 'Unknown Store'),
                site_id=store['site_id']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

@router.get("/stores/{store_id}/orders/{order_id}")
async def get_ml_order_detail(
    store_id: int,
    order_id: str,
    current_user: AuthData = Depends(verify_token)
) -> dict:
    """
    Get detailed information about a specific ML order.
    """
    
    try:
        # Get valid access token
        access_token, store = await get_ml_access_token(store_id, current_user["user_id"])
        
        # Get order details from ML API
        url = f"https://api.mercadolibre.com/orders/{order_id}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                error_detail = response.json() if response.text else {}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ML API error: {error_detail.get('message', 'Order not found')}"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order detail: {str(e)}")

@router.get("/stores/{store_id}/user-info")
async def get_ml_user_info(
    store_id: int,
    current_user: AuthData = Depends(verify_token)
) -> dict:
    """
    Get ML user information for a connected store.
    """
    
    try:
        # Get valid access token
        access_token, store = await get_ml_access_token(store_id, current_user["user_id"])
        
        # Get user info from ML API
        user_info = await ml_oauth_service.get_user_info(access_token)
        
        # Update in database if needed
        if not store.get('ml_user_id') or store.get('ml_user_id') != user_info['id']:
            supabase.table('ml_accounts').update({
                'ml_user_id': user_info['id'],
                'ml_nickname': user_info.get('nickname')
            }).eq('id', store_id).execute()
        
        return {
            "id": user_info['id'],
            "nickname": user_info.get('nickname'),
            "email": user_info.get('email'),
            "country_id": user_info.get('country_id'),
            "site_id": store['site_id'],
            "store_name": store.get('nickname', 'Unknown Store'),
            "registration_date": user_info.get('registration_date'),
            "points": user_info.get('points', 0),
            "reputation": user_info.get('seller_reputation', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

@router.post("/stores/{store_id}/sync-orders")
async def sync_ml_orders(
    store_id: int,
    current_user: AuthData = Depends(verify_token)
) -> dict:
    """
    Sync orders from ML to local database.
    """
    
    try:
        # Get valid access token
        access_token, store = await get_ml_access_token(store_id, current_user["user_id"])
        
        # Get recent orders
        ml_user_id = store.get('ml_user_id')
        if not ml_user_id:
            user_info = await ml_oauth_service.get_user_info(access_token)
            ml_user_id = user_info['id']
        
        url = f"https://api.mercadolibre.com/orders/search"
        params = {
            'seller': ml_user_id,
            'offset': 0,
            'limit': 100,
            'sort': 'date_desc'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch orders from ML"
                )
            
            data = response.json()
            orders_synced = 0
            
            # Save orders to database
            for order_data in data.get('results', []):
                # Check if order exists
                existing = supabase.table('ml_orders').select("id").eq(
                    'ml_order_id', order_data['id']
                ).execute()
                
                order_record = {
                    'ml_order_id': order_data['id'],
                    'store_id': store_id,
                    'user_id': current_user["user_id"],
                    'status': order_data['status'],
                    'total_amount': order_data['total_amount'],
                    'currency_id': order_data['currency_id'],
                    'buyer_nickname': order_data['buyer']['nickname'],
                    'date_created': order_data['date_created'],
                    'order_data': order_data,  # Store full JSON
                    'synced_at': datetime.now().isoformat()
                }
                
                if existing.data:
                    # Update existing order
                    supabase.table('ml_orders').update(order_record).eq(
                        'ml_order_id', order_data['id']
                    ).execute()
                else:
                    # Insert new order
                    supabase.table('ml_orders').insert(order_record).execute()
                
                orders_synced += 1
            
            return {
                "status": "success",
                "orders_synced": orders_synced,
                "total_orders": data.get('paging', {}).get('total', 0),
                "message": f"Synchronized {orders_synced} orders successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")