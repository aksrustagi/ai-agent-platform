"""Mem0 client for persistent agent memory."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import Settings
from backend.utils.errors import MemoryError
from backend.utils.logger import get_logger
from backend.utils.security import mask_sensitive_data

logger = get_logger(__name__)


class Mem0Client:
    """
    Client for interacting with Mem0 API for persistent memory.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize Mem0 client.
        
        Args:
            settings: Application settings
        """
        self.api_key = settings.mem0_api_key
        self.base_url = settings.mem0_base_url
        self.timeout = settings.retry_timeout
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )
        
        logger.info(
            "Mem0 client initialized",
            base_url=self.base_url,
            api_key=mask_sensitive_data(self.api_key)
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("Mem0 client closed")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def add_memory(
        self,
        user_id: str,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a memory to Mem0.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            content: Memory content
            metadata: Optional metadata
            category: Optional category
        
        Returns:
            Created memory object
        
        Raises:
            MemoryError: If memory creation fails
        """
        try:
            payload = {
                "user_id": user_id,
                "agent_id": agent_id,
                "content": content,
                "metadata": metadata or {},
                "category": category
            }
            
            logger.debug(
                "Adding memory to Mem0",
                user_id=user_id,
                agent_id=agent_id,
                category=category
            )
            
            response = await self.client.post("/memories", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "Memory added successfully",
                memory_id=result.get("id"),
                user_id=user_id,
                agent_id=agent_id
            )
            
            return result
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to add memory",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to add memory: {e.response.status_code}",
                details={"status_code": e.response.status_code, "response": e.response.text}
            )
        except Exception as e:
            logger.error("Unexpected error adding memory", error=str(e))
            raise MemoryError(f"Unexpected error adding memory: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def search_memories(
        self,
        user_id: str,
        query: str,
        agent_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories in Mem0.
        
        Args:
            user_id: User ID
            query: Search query
            agent_id: Optional agent ID filter
            category: Optional category filter
            limit: Maximum number of results
        
        Returns:
            List of matching memories
        
        Raises:
            MemoryError: If search fails
        """
        try:
            params = {
                "user_id": user_id,
                "query": query,
                "limit": limit
            }
            
            if agent_id:
                params["agent_id"] = agent_id
            if category:
                params["category"] = category
            
            logger.debug(
                "Searching memories in Mem0",
                user_id=user_id,
                agent_id=agent_id,
                query=query[:50]  # Log first 50 chars
            )
            
            response = await self.client.get("/memories/search", params=params)
            response.raise_for_status()
            
            results = response.json()
            memories = results.get("memories", [])
            
            logger.info(
                "Memory search completed",
                user_id=user_id,
                results_count=len(memories)
            )
            
            return memories
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to search memories",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to search memories: {e.response.status_code}",
                details={"status_code": e.response.status_code, "response": e.response.text}
            )
        except Exception as e:
            logger.error("Unexpected error searching memories", error=str(e))
            raise MemoryError(f"Unexpected error searching memories: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Memory ID
        
        Returns:
            Memory object
        
        Raises:
            MemoryError: If retrieval fails
        """
        try:
            logger.debug("Retrieving memory from Mem0", memory_id=memory_id)
            
            response = await self.client.get(f"/memories/{memory_id}")
            response.raise_for_status()
            
            memory = response.json()
            
            logger.info("Memory retrieved successfully", memory_id=memory_id)
            
            return memory
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to retrieve memory",
                memory_id=memory_id,
                status_code=e.response.status_code,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to retrieve memory: {e.response.status_code}",
                details={"memory_id": memory_id, "status_code": e.response.status_code}
            )
        except Exception as e:
            logger.error("Unexpected error retrieving memory", error=str(e))
            raise MemoryError(f"Unexpected error retrieving memory: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: Memory ID
        
        Returns:
            True if successful
        
        Raises:
            MemoryError: If deletion fails
        """
        try:
            logger.debug("Deleting memory from Mem0", memory_id=memory_id)
            
            response = await self.client.delete(f"/memories/{memory_id}")
            response.raise_for_status()
            
            logger.info("Memory deleted successfully", memory_id=memory_id)
            
            return True
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to delete memory",
                memory_id=memory_id,
                status_code=e.response.status_code,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to delete memory: {e.response.status_code}",
                details={"memory_id": memory_id, "status_code": e.response.status_code}
            )
        except Exception as e:
            logger.error("Unexpected error deleting memory", error=str(e))
            raise MemoryError(f"Unexpected error deleting memory: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def list_memories(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List memories for a user.
        
        Args:
            user_id: User ID
            agent_id: Optional agent ID filter
            category: Optional category filter
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of memories
        
        Raises:
            MemoryError: If listing fails
        """
        try:
            params = {
                "user_id": user_id,
                "limit": limit,
                "offset": offset
            }
            
            if agent_id:
                params["agent_id"] = agent_id
            if category:
                params["category"] = category
            
            logger.debug(
                "Listing memories from Mem0",
                user_id=user_id,
                agent_id=agent_id,
                category=category
            )
            
            response = await self.client.get("/memories", params=params)
            response.raise_for_status()
            
            results = response.json()
            memories = results.get("memories", [])
            
            logger.info(
                "Memories listed successfully",
                user_id=user_id,
                count=len(memories)
            )
            
            return memories
        
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to list memories",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to list memories: {e.response.status_code}",
                details={"status_code": e.response.status_code, "response": e.response.text}
            )
        except Exception as e:
            logger.error("Unexpected error listing memories", error=str(e))
            raise MemoryError(f"Unexpected error listing memories: {str(e)}")
