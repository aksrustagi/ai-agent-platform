"""Global tool registry for managing all available tools across agents."""

from typing import Any, Callable, Dict, List, Optional

from backend.integrations.mcp_client import MCPClient
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """
    Global registry for managing tools across all agents.
    Provides centralized tool registration, discovery, and execution.
    """
    
    def __init__(self) -> None:
        """Initialize tool registry."""
        self.mcp_client = MCPClient()
        self._agent_tools: Dict[str, List[str]] = {}
        logger.info("Tool registry initialized")
    
    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        category: Optional[str] = None,
        agents: Optional[List[str]] = None,
        requires_confirmation: bool = False
    ) -> None:
        """
        Register a tool in the global registry.
        
        Args:
            name: Tool name
            description: Tool description
            function: Callable to execute
            parameters: JSON schema for parameters
            category: Optional category
            agents: List of agent IDs that can use this tool
            requires_confirmation: Whether tool requires confirmation
        """
        # Register with MCP client
        self.mcp_client.register_tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            requires_confirmation=requires_confirmation
        )
        
        # Track which agents can use this tool
        if agents:
            for agent_id in agents:
                if agent_id not in self._agent_tools:
                    self._agent_tools[agent_id] = []
                self._agent_tools[agent_id].append(name)
        
        logger.info(f"Registered tool: {name}", agents=agents, category=category)
    
    def register_tool_from_function(
        self,
        function: Callable,
        category: Optional[str] = None,
        agents: Optional[List[str]] = None,
        requires_confirmation: bool = False
    ) -> None:
        """
        Register a tool from a function.
        
        Args:
            function: Function to register
            category: Optional category
            agents: List of agent IDs that can use this tool
            requires_confirmation: Whether tool requires confirmation
        """
        self.mcp_client.register_tool_from_function(
            function=function,
            category=category,
            requires_confirmation=requires_confirmation
        )
        
        name = function.__name__
        
        # Track which agents can use this tool
        if agents:
            for agent_id in agents:
                if agent_id not in self._agent_tools:
                    self._agent_tools[agent_id] = []
                self._agent_tools[agent_id].append(name)
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            agent_id: Optional agent ID for access control
        
        Returns:
            Execution result
        """
        # Check if agent has access to this tool
        if agent_id and agent_id in self._agent_tools:
            if tool_name not in self._agent_tools[agent_id]:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} does not have access to tool {tool_name}",
                    "tool_name": tool_name
                }
        
        return await self.mcp_client.execute_tool(tool_name, parameters)
    
    def get_tools_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all tools available to a specific agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            List of tool schemas
        """
        if agent_id not in self._agent_tools:
            return []
        
        tool_names = self._agent_tools[agent_id]
        return self.mcp_client.get_tools_schema(tool_names=tool_names)
    
    def get_all_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all registered tools.
        
        Args:
            category: Optional category filter
        
        Returns:
            List of tool schemas
        """
        return self.mcp_client.get_tools_schema(category=category)
    
    def list_agent_tools(self, agent_id: str) -> List[str]:
        """List tool names available to an agent."""
        return self._agent_tools.get(agent_id, [])
    
    def list_all_tools(self, category: Optional[str] = None) -> List[str]:
        """List all tool names."""
        return self.mcp_client.list_tools(category=category)
    
    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return self.mcp_client.list_categories()
    
    def assign_tool_to_agent(self, tool_name: str, agent_id: str) -> bool:
        """
        Assign an existing tool to an agent.
        
        Args:
            tool_name: Name of tool
            agent_id: Agent identifier
        
        Returns:
            True if successful
        """
        if tool_name not in self.mcp_client.tools:
            return False
        
        if agent_id not in self._agent_tools:
            self._agent_tools[agent_id] = []
        
        if tool_name not in self._agent_tools[agent_id]:
            self._agent_tools[agent_id].append(tool_name)
        
        logger.info(f"Assigned tool {tool_name} to agent {agent_id}")
        return True
    
    def unassign_tool_from_agent(self, tool_name: str, agent_id: str) -> bool:
        """
        Unassign a tool from an agent.
        
        Args:
            tool_name: Name of tool
            agent_id: Agent identifier
        
        Returns:
            True if successful
        """
        if agent_id not in self._agent_tools:
            return False
        
        if tool_name in self._agent_tools[agent_id]:
            self._agent_tools[agent_id].remove(tool_name)
            logger.info(f"Unassigned tool {tool_name} from agent {agent_id}")
            return True
        
        return False


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def reset_tool_registry() -> None:
    """Reset the global tool registry (useful for testing)."""
    global _global_registry
    _global_registry = None
