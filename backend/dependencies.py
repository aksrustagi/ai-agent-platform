"""FastAPI dependency injection."""

from functools import lru_cache
from typing import Generator, Optional

from backend.config import Settings, get_settings
from backend.coordinator.agent_coordinator import AgentCoordinator
from backend.integrations.go_services_client import GoServicesClient
from backend.integrations.mcp_client import MCPClient
from backend.integrations.mediamagic_client import MediaMagicClient
from backend.memory.memory_manager import MemoryManager
from backend.services.llm_service import LLMService


# Global instances
_llm_service: Optional[LLMService] = None
_memory_manager: Optional[MemoryManager] = None
_agent_coordinator: Optional[AgentCoordinator] = None
_mcp_client: Optional[MCPClient] = None
_mediamagic_client: Optional[MediaMagicClient] = None
_go_services_client: Optional[GoServicesClient] = None


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


def get_mcp_client() -> MCPClient:
    """Get MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        settings = get_cached_settings()
        _mcp_client = MCPClient(enable_remote=settings.mcp_enable_remote)
        
        # Add configured MCP servers
        if settings.mcp_server_url:
            _mcp_client.add_server(
                name="default",
                base_url=settings.mcp_server_url,
                description="Default MCP server"
            )
        
        if settings.mediamagic_api_url:
            _mcp_client.add_server(
                name="mediamagic",
                base_url=settings.mediamagic_api_url,
                api_key=settings.mediamagic_api_key,
                description="MediaMagic API for media processing"
            )
        
        if settings.go_services_url:
            _mcp_client.add_server(
                name="go-services",
                base_url=settings.go_services_url,
                api_key=settings.go_services_api_key,
                description="Go microservices"
            )
    
    return _mcp_client


def get_mediamagic_client() -> Optional[MediaMagicClient]:
    """Get MediaMagic client instance."""
    global _mediamagic_client
    settings = get_cached_settings()
    
    if not settings.mediamagic_api_url:
        return None
    
    if _mediamagic_client is None:
        _mediamagic_client = MediaMagicClient(
            base_url=settings.mediamagic_api_url,
            api_key=settings.mediamagic_api_key
        )
    
    return _mediamagic_client


def get_go_services_client() -> Optional[GoServicesClient]:
    """Get Go Services client instance."""
    global _go_services_client
    settings = get_cached_settings()
    
    if not settings.go_services_url:
        return None
    
    if _go_services_client is None:
        _go_services_client = GoServicesClient(
            base_url=settings.go_services_url,
            api_key=settings.go_services_api_key
        )
    
    return _go_services_client
