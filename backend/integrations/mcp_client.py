"""Enhanced MCP (Model Context Protocol) client for agent tool integration."""

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class Tool:
    """Represents a tool that can be called by an agent."""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        category: Optional[str] = None,
        requires_confirmation: bool = False
    ) -> None:
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
        self.category = category
        self.requires_confirmation = requires_confirmation
        
        # Store if function is async
        self.is_async = asyncio.iscoroutinefunction(function)
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        try:
            if self.is_async:
                result = await self.function(**kwargs)
            else:
                result = self.function(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {self.name}", error=str(e))
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema in format compatible with LLM providers."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }


class MCPClient:
    """
    Enhanced Model Context Protocol client for agent tool integration.
    Provides proper tool registration, execution, and schema management.
    """
    
    def __init__(self) -> None:
        """Initialize MCP client."""
        self.tools: Dict[str, Tool] = {}
        self.tool_categories: Dict[str, List[str]] = {}
        logger.info("Enhanced MCP client initialized")
    
    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any],
        category: Optional[str] = None,
        requires_confirmation: bool = False
    ) -> None:
        """
        Register a tool for MCP.
        
        Args:
            name: Tool name
            description: Tool description
            function: Callable function to execute
            parameters: JSON schema for tool parameters
            category: Optional category for tool organization
            requires_confirmation: Whether tool requires user confirmation
        """
        tool = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            requires_confirmation=requires_confirmation
        )
        
        self.tools[name] = tool
        
        # Update category index
        if category:
            if category not in self.tool_categories:
                self.tool_categories[category] = []
            self.tool_categories[category].append(name)
        
        logger.info(f"Registered MCP tool: {name}", category=category)
    
    def register_tool_from_function(
        self,
        function: Callable,
        category: Optional[str] = None,
        requires_confirmation: bool = False
    ) -> None:
        """
        Register a tool from a function with type hints and docstring.
        
        Args:
            function: Function to register as tool
            category: Optional category
            requires_confirmation: Whether tool requires confirmation
        """
        # Extract function metadata
        name = function.__name__
        description = function.__doc__ or f"Execute {name}"
        
        # Build parameters schema from type hints
        sig = inspect.signature(function)
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
            
            param_type = "string"  # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"
            
            parameters["properties"][param_name] = {"type": param_type}
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
        
        self.register_tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            requires_confirmation=requires_confirmation
        )
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a registered tool.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
        
        Returns:
            Execution result with success status and data
        """
        if tool_name not in self.tools:
            error_msg = f"Tool {tool_name} not found"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name
            }
        
        tool = self.tools[tool_name]
        
        logger.info(f"Executing MCP tool: {tool_name}", parameters=parameters)
        
        try:
            result = await tool.execute(**parameters)
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name}", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def get_tools_schema(
        self,
        category: Optional[str] = None,
        tool_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get schema for registered tools.
        
        Args:
            category: Optional filter by category
            tool_names: Optional filter by specific tool names
        
        Returns:
            List of tool schemas
        """
        tools_to_include = []
        
        if tool_names:
            tools_to_include = [self.tools[name] for name in tool_names if name in self.tools]
        elif category:
            tool_names_in_category = self.tool_categories.get(category, [])
            tools_to_include = [self.tools[name] for name in tool_names_in_category]
        else:
            tools_to_include = list(self.tools.values())
        
        return [tool.get_schema() for tool in tools_to_include]
    
    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all registered tool names, optionally filtered by category."""
        if category:
            return self.tool_categories.get(category, [])
        return list(self.tools.keys())
    
    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(self.tool_categories.keys())
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of tool to unregister
        
        Returns:
            True if tool was unregistered, False if not found
        """
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        
        # Remove from category index
        if tool.category and tool.category in self.tool_categories:
            self.tool_categories[tool.category].remove(tool_name)
            if not self.tool_categories[tool.category]:
                del self.tool_categories[tool.category]
        
        # Remove tool
        del self.tools[tool_name]
        
        logger.info(f"Unregistered tool: {tool_name}")
        return True
