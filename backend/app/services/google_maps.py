"""Google Maps Service for Geolocation and Geocoding."""

from __future__ import annotations

import logging
from typing import Optional, Tuple, Dict, Any

import httpx
from ..core.config import settings

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Client for Google Maps Platform APIs."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.google_maps_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        await self.client.aclose()

    async def get_address_from_coordinates(self, lat: float, lng: float) -> str | None:
        """Reverse geocoding: Get address from lat/lng."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured.")
            return None

        try:
            url = f"{self.base_url}/geocode/json"
            params = {"latlng": f"{lat},{lng}", "key": self.api_key}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and data["results"]:
                return data["results"][0]["formatted_address"]
            else:
                logger.warning(f"Google Geocoding failed: {data.get('status')}")
                return None
        except Exception as e:
            logger.error(f"Error in reverse geocoding: {e}")
            return None

    async def get_coordinates_from_address(self, address: str) -> Tuple[float, float] | None:
        """Geocoding: Get lat/lng from address."""
        if not self.api_key:
            logger.warning("Google Maps API key not configured.")
            return None

        try:
            url = f"{self.base_url}/geocode/json"
            params = {"address": address, "key": self.api_key}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return location["lat"], location["lng"]
            else:
                logger.warning(f"Google Geocoding failed: {data.get('status')}")
                return None
        except Exception as e:
            logger.error(f"Error in geocoding: {e}")
            return None

    async def get_place_details(self, place_id: str) -> Dict[str, Any] | None:
        """Get details for a specific place ID."""
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/place/details/json"
            params = {"place_id": place_id, "key": self.api_key}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK":
                return data["result"]
            return None
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None


# Global instance
google_maps_service = GoogleMapsService()
