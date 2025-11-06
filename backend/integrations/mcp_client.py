"""MCP (Model Context Protocol) client wrapper."""

from typing import Any, Dict, List, Optional

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MCPClient:
    """
    Model Context Protocol client for agent tool integration.
    This is a simplified wrapper for MCP functionality.
    """
    
    def __init__(self) -> None:
        logger.info("MCP client initialized")
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: callable
    ) -> None:
        """Register a tool for MCP."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": function
        }
        logger.info(f"Registered MCP tool: {name}")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        function = tool["function"]
        
        logger.info(f"Executing MCP tool: {tool_name}")
        
        if asyncio.iscoroutinefunction(function):
            result = await function(**parameters)
        else:
            result = function(**parameters)
        
        return result
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get schema for all registered tools."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools.values()
        ]


import asyncio
