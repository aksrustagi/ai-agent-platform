"""FastAPI dependency injection."""

from functools import lru_cache
from typing import Generator

from backend.config import Settings, get_settings
from backend.coordinator.agent_coordinator import AgentCoordinator
from backend.memory.memory_manager import MemoryManager
from backend.services.llm_service import LLMService


# Global instances
_llm_service: LLMService | None = None
_memory_manager: MemoryManager | None = None
_agent_coordinator: AgentCoordinator | None = None


@lru_cache()
def get_cached_settings() -> Settings:
    """Get cached settings instance."""
    return get_settings()


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    global _llm_service
    if _llm_service is None:
        settings = get_cached_settings()
        _llm_service = LLMService(settings)
    return _llm_service


def get_memory_manager() -> MemoryManager:
    """Get memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        settings = get_cached_settings()
        _memory_manager = MemoryManager(settings)
    return _memory_manager


def get_agent_coordinator() -> AgentCoordinator:
    """Get agent coordinator instance."""
    global _agent_coordinator
    if _agent_coordinator is None:
        settings = get_cached_settings()
        llm_service = get_llm_service()
        memory_manager = get_memory_manager()
        _agent_coordinator = AgentCoordinator(settings, llm_service, memory_manager)
    return _agent_coordinator
