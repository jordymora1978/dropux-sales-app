"""
MercadoLibre OAuth and API integration service
"""
import os
import httpx
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class MercadoLibreService:
    def __init__(self):
        self.client_id = os.getenv("ML_CLIENT_ID")
        self.client_secret = os.getenv("ML_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ML_REDIRECT_URI", "https://sales.dropux.co/todoencargo/ml/callback")
        self.base_url = "https://api.mercadolibre.com"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("ML_CLIENT_ID and ML_CLIENT_SECRET environment variables are required")
    
    def get_auth_url(self, site_id: str = "MCO") -> str:
        """
        Generate authorization URL for MercadoLibre OAuth
        
        Args:
            site_id: MercadoLibre site (MCO=Colombia, MLA=Argentina, etc.)
        
        Returns:
            Authorization URL string
        """
        return (
            f"https://auth.mercadolibre.com.co/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={site_id}"
        )
    
    async def exchange_code_for_tokens(self, code: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dictionary with access_token, refresh_token, etc.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Dictionary with new access_token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from MercadoLibre
        
        Args:
            access_token: Valid access token
            
        Returns:
            User information dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_orders(self, access_token: str, seller_id: str, limit: int = 50, offset: int = 0) -> Dict:
        """
        Get orders for a seller
        
        Args:
            access_token: Valid access token
            seller_id: MercadoLibre seller ID
            limit: Number of orders to fetch
            offset: Offset for pagination
            
        Returns:
            Orders data dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders/search",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "seller": seller_id,
                    "limit": limit,
                    "offset": offset
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_order_details(self, access_token: str, order_id: str) -> Dict:
        """
        Get detailed information for a specific order
        
        Args:
            access_token: Valid access token
            order_id: MercadoLibre order ID
            
        Returns:
            Detailed order information
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/orders/{order_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()