"""Go Services client for microservices communication."""

from typing import Any, Dict, List, Optional

import httpx

from backend.utils.errors import IntegrationError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class GoServicesClient:
    """
    Client for Go microservices integration.
    Provides access to various Go-based backend services.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize Go Services client.
        
        Args:
            base_url: Go Services base URL
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self._http_client: Optional[httpx.AsyncClient] = None
        logger.info(f"Go Services client initialized: {self.base_url}")
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def call_service(
        self,
        service_name: str,
        method: str,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Call a Go microservice method.
        
        Args:
            service_name: Name of the service
            method: Method to call
            payload: Request payload
            timeout: Optional custom timeout
        
        Returns:
            Service response
        """
        try:
            client = await self._get_http_client()
            
            response = await client.post(
                f"{self.base_url}/api/v1/services/{service_name}/{method}",
                json=payload,
                headers=self._get_headers(),
                timeout=timeout or 30.0
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Go service called: {service_name}.{method}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Go service call failed: {e}")
            raise IntegrationError(
                message=f"Failed to call Go service: {service_name}.{method}",
                details={"error": str(e), "service": service_name, "method": method}
            )
    
    async def data_service_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the data service.
        
        Args:
            query: Query string
            parameters: Optional query parameters
        
        Returns:
            Query results
        """
        return await self.call_service(
            service_name="data",
            method="query",
            payload={"query": query, "parameters": parameters or {}}
        )
    
    async def cache_service_get(self, key: str) -> Dict[str, Any]:
        """
        Get value from cache service.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        return await self.call_service(
            service_name="cache",
            method="get",
            payload={"key": key}
        )
    
    async def cache_service_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Set value in cache service.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL in seconds
        
        Returns:
            Success status
        """
        payload = {"key": key, "value": value}
        if ttl is not None:
            payload["ttl"] = ttl
        
        return await self.call_service(
            service_name="cache",
            method="set",
            payload=payload
        )
    
    async def storage_service_upload(
        self,
        file_name: str,
        content: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to storage service.
        
        Args:
            file_name: Name of the file
            content: File content as bytes
            content_type: MIME type
            metadata: Optional metadata
        
        Returns:
            Upload result with file URL
        """
        try:
            client = await self._get_http_client()
            
            files = {
                "file": (file_name, content, content_type)
            }
            
            data = {}
            if metadata:
                data["metadata"] = metadata
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.post(
                f"{self.base_url}/api/v1/services/storage/upload",
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"File uploaded: {file_name}")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"File upload failed: {e}")
            raise IntegrationError(
                message="Failed to upload file",
                details={"error": str(e), "file_name": file_name}
            )
    
    async def notification_service_send(
        self,
        recipient: str,
        channel: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification via notification service.
        
        Args:
            recipient: Recipient identifier (email, phone, user_id)
            channel: Notification channel (email, sms, push)
            message: Message content
            metadata: Optional metadata
        
        Returns:
            Send result
        """
        return await self.call_service(
            service_name="notification",
            method="send",
            payload={
                "recipient": recipient,
                "channel": channel,
                "message": message,
                "metadata": metadata or {}
            }
        )
    
    async def analytics_service_track_event(
        self,
        event_name: str,
        user_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track analytics event.
        
        Args:
            event_name: Name of the event
            user_id: User identifier
            properties: Optional event properties
        
        Returns:
            Tracking result
        """
        return await self.call_service(
            service_name="analytics",
            method="track",
            payload={
                "event_name": event_name,
                "user_id": user_id,
                "properties": properties or {}
            }
        )
    
    async def auth_service_validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate
        
        Returns:
            Validation result with user info
        """
        return await self.call_service(
            service_name="auth",
            method="validate",
            payload={"token": token}
        )
    
    async def queue_service_enqueue(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 0
    ) -> Dict[str, Any]:
        """
        Enqueue a message to a queue.
        
        Args:
            queue_name: Name of the queue
            message: Message to enqueue
            priority: Message priority (0-10)
        
        Returns:
            Enqueue result
        """
        return await self.call_service(
            service_name="queue",
            method="enqueue",
            payload={
                "queue_name": queue_name,
                "message": message,
                "priority": priority
            }
        )
    
    async def list_services(self) -> List[Dict[str, Any]]:
        """
        List all available Go services.
        
        Returns:
            List of available services and their methods
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/api/v1/services",
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            services = response.json()
            logger.info(f"Retrieved {len(services)} Go services")
            
            return services
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to list services: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of Go services.
        
        Returns:
            Health status of all services
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/health",
                headers=self._get_headers(),
                timeout=10.0
            )
            response.raise_for_status()
            
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
