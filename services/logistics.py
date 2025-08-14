"""
Logistics providers integration service (Anicam & Chilexpress APIs)
"""
import httpx
from typing import Dict, Optional
from abc import ABC, abstractmethod

class LogisticsProvider(ABC):
    """Abstract base class for logistics providers"""
    
    @abstractmethod
    async def get_tracking_info(self, tracking_number: str) -> Dict:
        """Get tracking information for a shipment"""
        pass
    
    @abstractmethod
    async def create_shipment(self, shipment_data: Dict) -> Dict:
        """Create a new shipment"""
        pass

class AnicamService(LogisticsProvider):
    """Anicam logistics provider service"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.anicam.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_tracking_info(self, tracking_number: str) -> Dict:
        """
        Get tracking information from Anicam
        
        Args:
            tracking_number: Tracking number to query
            
        Returns:
            Tracking information dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tracking/{tracking_number}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def create_shipment(self, shipment_data: Dict) -> Dict:
        """
        Create a new shipment with Anicam
        
        Args:
            shipment_data: Shipment information
            
        Returns:
            Created shipment information
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/shipments",
                headers=self.headers,
                json=shipment_data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_shipping_rates(self, origin: str, destination: str, weight: float) -> Dict:
        """
        Get shipping rates from Anicam
        
        Args:
            origin: Origin address/code
            destination: Destination address/code
            weight: Package weight in kg
            
        Returns:
            Shipping rates information
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rates",
                headers=self.headers,
                json={
                    "origin": origin,
                    "destination": destination,
                    "weight": weight
                }
            )
            response.raise_for_status()
            return response.json()

class ChilexpressService(LogisticsProvider):
    """Chilexpress logistics provider service"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.chilexpress.cl"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_tracking_info(self, tracking_number: str) -> Dict:
        """
        Get tracking information from Chilexpress
        
        Args:
            tracking_number: Tracking number to query
            
        Returns:
            Tracking information dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/tracking/{tracking_number}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def create_shipment(self, shipment_data: Dict) -> Dict:
        """
        Create a new shipment with Chilexpress
        
        Args:
            shipment_data: Shipment information
            
        Returns:
            Created shipment information
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/shipments",
                headers=self.headers,
                json=shipment_data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_shipping_rates(self, origin: str, destination: str, weight: float) -> Dict:
        """
        Get shipping rates from Chilexpress
        
        Args:
            origin: Origin address/code
            destination: Destination address/code
            weight: Package weight in kg
            
        Returns:
            Shipping rates information
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/rates",
                headers=self.headers,
                json={
                    "origin": origin,
                    "destination": destination,
                    "weight": weight
                }
            )
            response.raise_for_status()
            return response.json()

class LogisticsServiceFactory:
    """Factory class to create logistics service instances"""
    
    @staticmethod
    def create_service(provider_name: str, credentials: Dict) -> LogisticsProvider:
        """
        Create a logistics service instance
        
        Args:
            provider_name: Name of the provider ("anicam" or "chilexpress")
            credentials: Provider credentials
            
        Returns:
            LogisticsProvider instance
        """
        provider_name = provider_name.lower()
        
        if provider_name == "anicam":
            return AnicamService(
                api_key=credentials["api_key"],
                base_url=credentials.get("base_url", "https://api.anicam.com")
            )
        elif provider_name == "chilexpress":
            return ChilexpressService(
                api_key=credentials["api_key"],
                base_url=credentials.get("base_url", "https://api.chilexpress.cl")
            )
        else:
            raise ValueError(f"Unsupported logistics provider: {provider_name}")