"""
MercadoLibre OAuth Service - Professional Multi-tenant Implementation
Handles ML app connections for individual users
"""

from datetime import datetime, timedelta
import json
import hashlib
import hmac
from typing import Optional, Dict, Any
import httpx
from fastapi import HTTPException
import os
from cryptography.fernet import Fernet
import base64

# Type aliases for Python 3.12+
type MLTokens = dict[str, str | int]
type MLUserInfo = dict[str, Any]
type StoreConfig = dict[str, str | int | None]

class MLOAuthService:
    """Professional MercadoLibre OAuth service with security best practices."""
    
    # ML OAuth endpoints by country
    ML_SITES = {
        'MLA': {'name': 'Argentina', 'domain': 'com.ar'},
        'MLB': {'name': 'Brasil', 'domain': 'com.br'},
        'MCO': {'name': 'Colombia', 'domain': 'com.co'},
        'MCR': {'name': 'Costa Rica', 'domain': 'co.cr'},
        'MEC': {'name': 'Ecuador', 'domain': 'com.ec'},
        'MLC': {'name': 'Chile', 'domain': 'cl'},
        'MLM': {'name': 'México', 'domain': 'com.mx'},
        'MLU': {'name': 'Uruguay', 'domain': 'com.uy'},
        'MLV': {'name': 'Venezuela', 'domain': 'com.ve'},
        'MPA': {'name': 'Panamá', 'domain': 'com.pa'},
        'MPE': {'name': 'Perú', 'domain': 'com.pe'},
        'MPT': {'name': 'Portugal', 'domain': 'pt'},
        'MRD': {'name': 'Dominicana', 'domain': 'com.do'}
    }
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize with optional encryption for secrets."""
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode()[:32].ljust(32, b'0'))
        else:
            # Generate a key from environment or default
            key = os.getenv('ENCRYPTION_KEY', 'dropux_default_key_2024')
            key_bytes = base64.urlsafe_b64encode(key.encode()[:32].ljust(32, b'0'))
            self.cipher = Fernet(key_bytes)
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt sensitive data before storing."""
        return self.cipher.encrypt(secret.encode()).decode()
    
    def decrypt_secret(self, encrypted: str) -> str:
        """Decrypt sensitive data when needed."""
        return self.cipher.decrypt(encrypted.encode()).decode()
    
    def validate_credentials(self, app_id: str, app_secret: str) -> bool:
        """Validate ML app credentials format."""
        # App ID should be numeric and 10-20 digits
        if not app_id.isdigit() or not (10 <= len(app_id) <= 20):
            return False
        
        # App secret should be alphanumeric and 20+ chars
        if len(app_secret) < 20:
            return False
            
        return True
    
    def generate_redirect_uri(self, user_id: int, site_id: str) -> str:
        """Generate unique redirect URI for this user's connection."""
        # Create a unique identifier for this connection
        unique_id = hashlib.md5(f"{user_id}_{site_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:10]
        
        # Use the professional domain
        base_url = os.getenv('APP_BASE_URL', 'https://api.dropux.co')
        return f"{base_url}/api/ml/callback/{unique_id}"
    
    def get_auth_url(self, site_id: str, client_id: str, redirect_uri: str, state: str) -> str:
        """Generate ML OAuth authorization URL."""
        if site_id not in self.ML_SITES:
            raise ValueError(f"Invalid site_id: {site_id}")
        
        domain = self.ML_SITES[site_id]['domain']
        
        # Professional OAuth URL with all required parameters
        auth_url = (
            f"https://auth.mercadolibre.{domain}/authorization?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"state={state}"
        )
        
        return auth_url
    
    async def exchange_code_for_tokens(
        self, 
        code: str, 
        client_id: str, 
        client_secret: str, 
        redirect_uri: str,
        site_id: str
    ) -> MLTokens:
        """Exchange authorization code for access and refresh tokens."""
        
        if site_id not in self.ML_SITES:
            raise ValueError(f"Invalid site_id: {site_id}")
        
        # ML token endpoint
        token_url = "https://api.mercadolibre.com/oauth/token"
        
        # Prepare request data
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        # Make request with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    token_url,
                    data=data,
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    raise HTTPException(
                        status_code=400,
                        detail=f"ML OAuth error: {error_data.get('message', 'Unknown error')}"
                    )
                
                tokens = response.json()
                
                # Validate response has required fields
                if 'access_token' not in tokens or 'refresh_token' not in tokens:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid token response from MercadoLibre"
                    )
                
                return tokens
                
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Timeout connecting to MercadoLibre"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error exchanging code: {str(e)}"
                )
    
    async def refresh_access_token(
        self, 
        refresh_token: str, 
        client_id: str, 
        client_secret: str,
        site_id: str
    ) -> MLTokens:
        """Refresh an expired access token."""
        
        token_url = "https://api.mercadolibre.com/oauth/token"
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    token_url,
                    data=data,
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=401,
                        detail="Failed to refresh token"
                    )
                
                return response.json()
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error refreshing token: {str(e)}"
                )
    
    async def get_user_info(self, access_token: str) -> MLUserInfo:
        """Get ML user information using access token."""
        
        url = "https://api.mercadolibre.com/users/me"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    url,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json'
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid or expired access token"
                    )
                
                return response.json()
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error getting user info: {str(e)}"
                )
    
    def validate_state_token(self, state: str, expected_user_id: int) -> bool:
        """Validate the state parameter to prevent CSRF attacks."""
        try:
            # Decode state (should contain user_id and timestamp)
            decoded = base64.b64decode(state).decode()
            parts = decoded.split('_')
            
            if len(parts) != 3:
                return False
            
            user_id, timestamp, signature = parts
            
            # Verify user_id matches
            if int(user_id) != expected_user_id:
                return False
            
            # Verify timestamp is recent (within 1 hour)
            token_time = datetime.fromisoformat(timestamp)
            if datetime.now() - token_time > timedelta(hours=1):
                return False
            
            # Verify signature
            expected_sig = hashlib.sha256(f"{user_id}_{timestamp}_dropux".encode()).hexdigest()[:10]
            if signature != expected_sig:
                return False
            
            return True
            
        except Exception:
            return False
    
    def generate_state_token(self, user_id: int) -> str:
        """Generate secure state token for OAuth flow."""
        timestamp = datetime.now().isoformat()
        signature = hashlib.sha256(f"{user_id}_{timestamp}_dropux".encode()).hexdigest()[:10]
        state = f"{user_id}_{timestamp}_{signature}"
        return base64.b64encode(state.encode()).decode()

# Singleton instance
ml_oauth_service = MLOAuthService()