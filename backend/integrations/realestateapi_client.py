"""RealEstateAPI.com client for property data."""

from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import Settings
from backend.utils.errors import IntegrationError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RealEstateAPIClient:
    """Client for RealEstateAPI.com."""
    
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.realestate_api_key
        self.base_url = settings.realestate_base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
        logger.info("RealEstateAPI client initialized")
    
    async def close(self) -> None:
        await self.client.aclose()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search_properties(
        self,
        location: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        property_type: Optional[str] = None,
        beds: Optional[int] = None,
        baths: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search properties."""
        try:
            params = {"location": location, "limit": limit}
            if min_price:
                params["min_price"] = min_price
            if max_price:
                params["max_price"] = max_price
            if property_type:
                params["property_type"] = property_type
            if beds:
                params["beds"] = beds
            if baths:
                params["baths"] = baths
            
            response = await self.client.get("/properties/search", params=params)
            response.raise_for_status()
            return response.json().get("properties", [])
        except Exception as e:
            logger.error(f"Property search failed: {e}")
            raise IntegrationError(f"Property search failed: {e}", integration="realestate_api")
    
    async def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """Get property details by ID."""
        try:
            response = await self.client.get(f"/properties/{property_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise IntegrationError(f"Get property failed: {e}", integration="realestate_api")
    
    async def get_market_stats(self, location: str) -> Dict[str, Any]:
        """Get market statistics for a location."""
        try:
            response = await self.client.get(f"/market/stats", params={"location": location})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise IntegrationError(f"Get market stats failed: {e}", integration="realestate_api")
