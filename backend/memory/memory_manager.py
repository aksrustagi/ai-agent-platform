"""Memory manager abstracting memory operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import Settings
from backend.memory.mem0_client import Mem0Client
from backend.models.responses import MemoryItem
from backend.utils.helpers import measure_time
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """
    High-level memory manager for agent memory operations.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize memory manager.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.mem0_client = Mem0Client(settings)
        
        logger.info("Memory manager initialized")
    
    async def close(self) -> None:
        """Close memory clients."""
        await self.mem0_client.close()
        logger.info("Memory manager closed")
    
    @measure_time
    async def add_memory(
        self,
        user_id: str,
        agent_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None
    ) -> MemoryItem:
        """
        Add a memory for an agent.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            content: Memory content
            metadata: Optional metadata
            category: Optional category
        
        Returns:
            Created memory item
        """
        logger.info(
            "Adding memory",
            user_id=user_id,
            agent_id=agent_id,
            category=category
        )
        
        memory_data = await self.mem0_client.add_memory(
            user_id=user_id,
            agent_id=agent_id,
            content=content,
            metadata=metadata,
            category=category
        )
        
        return self._convert_to_memory_item(memory_data)
    
    @measure_time
    async def search_memories(
        self,
        user_id: str,
        query: str,
        agent_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """
        Search memories for a user.
        
        Args:
            user_id: User ID
            query: Search query
            agent_id: Optional agent ID filter
            category: Optional category filter
            limit: Maximum number of results
        
        Returns:
            List of matching memory items
        """
        logger.info(
            "Searching memories",
            user_id=user_id,
            agent_id=agent_id,
            query=query[:50]
        )
        
        memories = await self.mem0_client.search_memories(
            user_id=user_id,
            query=query,
            agent_id=agent_id,
            category=category,
            limit=limit
        )
        
        return [self._convert_to_memory_item(m) for m in memories]
    
    @measure_time
    async def get_recent_memories(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        limit: int = 20
    ) -> List[MemoryItem]:
        """
        Get recent memories for a user.
        
        Args:
            user_id: User ID
            agent_id: Optional agent ID filter
            limit: Maximum number of results
        
        Returns:
            List of recent memory items
        """
        logger.info(
            "Getting recent memories",
            user_id=user_id,
            agent_id=agent_id,
            limit=limit
        )
        
        memories = await self.mem0_client.list_memories(
            user_id=user_id,
            agent_id=agent_id,
            limit=limit,
            offset=0
        )
        
        return [self._convert_to_memory_item(m) for m in memories]
    
    @measure_time
    async def get_context_for_agent(
        self,
        user_id: str,
        agent_id: str,
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_memories: int = 10
    ) -> str:
        """
        Get formatted context for an agent from memories.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            query: Optional search query
            categories: Optional category filters
            max_memories: Maximum memories to include
        
        Returns:
            Formatted context string
        """
        logger.info(
            "Building context for agent",
            user_id=user_id,
            agent_id=agent_id
        )
        
        all_memories: List[MemoryItem] = []
        
        # If query provided, search for relevant memories
        if query:
            searched_memories = await self.search_memories(
                user_id=user_id,
                query=query,
                agent_id=agent_id,
                limit=max_memories // 2
            )
            all_memories.extend(searched_memories)
        
        # Get recent memories as well
        recent_memories = await self.get_recent_memories(
            user_id=user_id,
            agent_id=agent_id,
            limit=max_memories // 2
        )
        all_memories.extend(recent_memories)
        
        # Deduplicate by ID
        seen_ids = set()
        unique_memories: List[MemoryItem] = []
        for mem in all_memories:
            if mem.id not in seen_ids:
                seen_ids.add(mem.id)
                unique_memories.append(mem)
        
        # Filter by categories if specified
        if categories:
            unique_memories = [
                m for m in unique_memories
                if m.category in categories
            ]
        
        # Limit to max_memories
        unique_memories = unique_memories[:max_memories]
        
        # Format as context string
        if not unique_memories:
            return "No relevant memories found."
        
        context_parts = ["**Relevant Context from Memory:**\n"]
        
        for memory in unique_memories:
            context_parts.append(f"• {memory.content}")
            if memory.category:
                context_parts[-1] += f" [Category: {memory.category}]"
        
        context = "\n".join(context_parts)
        
        logger.debug(
            "Context built",
            user_id=user_id,
            agent_id=agent_id,
            memory_count=len(unique_memories)
        )
        
        return context
    
    @measure_time
    async def store_conversation_context(
        self,
        user_id: str,
        agent_id: str,
        conversation_summary: str,
        key_facts: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[MemoryItem]:
        """
        Store conversation context as memories.
        
        Args:
            user_id: User ID
            agent_id: Agent ID
            conversation_summary: Summary of the conversation
            key_facts: List of key facts to remember
            metadata: Optional metadata
        
        Returns:
            List of created memory items
        """
        logger.info(
            "Storing conversation context",
            user_id=user_id,
            agent_id=agent_id,
            facts_count=len(key_facts)
        )
        
        created_memories: List[MemoryItem] = []
        
        # Store summary
        summary_memory = await self.add_memory(
            user_id=user_id,
            agent_id=agent_id,
            content=conversation_summary,
            metadata=metadata,
            category="conversation_summary"
        )
        created_memories.append(summary_memory)
        
        # Store each key fact
        for fact in key_facts:
            fact_memory = await self.add_memory(
                user_id=user_id,
                agent_id=agent_id,
                content=fact,
                metadata=metadata,
                category="key_fact"
            )
            created_memories.append(fact_memory)
        
        logger.info(
            "Conversation context stored",
            user_id=user_id,
            agent_id=agent_id,
            memories_created=len(created_memories)
        )
        
        return created_memories
    
    def _convert_to_memory_item(self, memory_data: Dict[str, Any]) -> MemoryItem:
        """
        Convert Mem0 memory data to MemoryItem.
        
        Args:
            memory_data: Raw memory data from Mem0
        
        Returns:
            MemoryItem instance
        """
        return MemoryItem(
            id=memory_data.get("id", ""),
            user_id=memory_data.get("user_id", ""),
            agent_id=memory_data.get("agent_id", ""),
            content=memory_data.get("content", ""),
            metadata=memory_data.get("metadata"),
            category=memory_data.get("category"),
            created_at=datetime.fromisoformat(
                memory_data.get("created_at", datetime.utcnow().isoformat())
            ),
            relevance_score=memory_data.get("relevance_score")
        )
