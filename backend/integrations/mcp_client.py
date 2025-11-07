"""MCP (Model Context Protocol) client wrapper with multi-server support."""

import asyncio
from typing import Any, Callable, Dict, List, Optional

import httpx

from backend.utils.errors import IntegrationError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MCPServer:
    """Configuration for an MCP server."""
    
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        description: Optional[str] = None
    ):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.description = description


class MCPClient:
    """
    Model Context Protocol client for agent tool integration.
    Supports both local tool registration and remote MCP server communication.
    """
    
    def __init__(self, enable_remote: bool = True) -> None:
        """
        Initialize MCP client.
        
        Args:
            enable_remote: Enable remote MCP server support
        """
        logger.info("MCP client initialized")
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.servers: Dict[str, MCPServer] = {}
        self.enable_remote = enable_remote
        self._http_client: Optional[httpx.AsyncClient] = None
    
    def add_server(
        self,
        name: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        description: Optional[str] = None
    ) -> None:
        """
        Add a remote MCP server configuration.
        
        Args:
            name: Server identifier
            base_url: Base URL of the MCP server
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            description: Server description
        """
        self.servers[name] = MCPServer(
            name=name,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            description=description
        )
        logger.info(f"Added MCP server: {name} ({base_url})")
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        function: Callable
    ) -> None:
        """
        Register a local tool for MCP.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Parameter schema
            function: Function to execute
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": function
        }
        logger.info(f"Registered MCP tool: {name}")
    
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
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        server: Optional[str] = None
    ) -> Any:
        """
        Execute a tool (local or remote).
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            server: Optional server name for remote execution
        
        Returns:
            Tool execution result
        """
        # Local tool execution
        if server is None and tool_name in self.tools:
            tool = self.tools[tool_name]
            function = tool["function"]
            
            logger.info(f"Executing local MCP tool: {tool_name}")
            
            if asyncio.iscoroutinefunction(function):
                result = await function(**parameters)
            else:
                result = function(**parameters)
            
            return result
        
        # Remote tool execution
        if server and server in self.servers:
            return await self._execute_remote_tool(tool_name, parameters, server)
        
        raise ValueError(f"Tool {tool_name} not found (server: {server})")
    
    async def _execute_remote_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        server: str
    ) -> Dict[str, Any]:
        """
        Execute a tool on a remote MCP server.
        
        Args:
            tool_name: Tool name
            parameters: Tool parameters
            server: Server name
        
        Returns:
            Execution result
        """
        if not self.enable_remote:
            raise IntegrationError(
                message="Remote MCP execution is disabled",
                details={"tool": tool_name}
            )
        
        mcp_server = self.servers[server]
        logger.info(f"Executing remote MCP tool: {tool_name} on {server}")
        
        try:
            client = await self._get_http_client()
            
            headers = {"Content-Type": "application/json"}
            if mcp_server.api_key:
                headers["Authorization"] = f"Bearer {mcp_server.api_key}"
            
            payload = {
                "tool": tool_name,
                "parameters": parameters
            }
            
            response = await client.post(
                f"{mcp_server.base_url}/mcp/execute",
                json=payload,
                headers=headers,
                timeout=mcp_server.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Remote tool {tool_name} executed successfully")
            
            return result
        
        except httpx.HTTPError as e:
            logger.error(f"Remote MCP tool execution failed: {e}")
            raise IntegrationError(
                message=f"Failed to execute remote MCP tool: {tool_name}",
                details={"error": str(e), "tool": tool_name, "server": server}
            )
    
    async def list_remote_tools(self, server: str) -> List[Dict[str, Any]]:
        """
        List available tools from a remote MCP server.
        
        Args:
            server: Server name
        
        Returns:
            List of available tools
        """
        if server not in self.servers:
            raise ValueError(f"Server {server} not found")
        
        mcp_server = self.servers[server]
        
        try:
            client = await self._get_http_client()
            
            headers = {}
            if mcp_server.api_key:
                headers["Authorization"] = f"Bearer {mcp_server.api_key}"
            
            response = await client.get(
                f"{mcp_server.base_url}/mcp/tools",
                headers=headers,
                timeout=mcp_server.timeout
            )
            response.raise_for_status()
            
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Failed to list remote tools: {e}")
            return []
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Get schema for all locally registered tools.
        
        Returns:
            List of tool schemas
        """
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools.values()
        ]
    
    def list_servers(self) -> List[Dict[str, Any]]:
        """
        List all configured MCP servers.
        
        Returns:
            List of server configurations
        """
        return [
            {
                "name": server.name,
                "base_url": server.base_url,
                "description": server.description,
                "has_api_key": server.api_key is not None
            }
            for server in self.servers.values()
        ]
    
    async def health_check(self, server: str) -> Dict[str, Any]:
        """
        Check health of a remote MCP server.
        
        Args:
            server: Server name
        
        Returns:
            Health status
        """
        if server not in self.servers:
            return {"healthy": False, "error": "Server not found"}
        
        mcp_server = self.servers[server]
        
        try:
            client = await self._get_http_client()
            
            headers = {}
            if mcp_server.api_key:
                headers["Authorization"] = f"Bearer {mcp_server.api_key}"
            
            response = await client.get(
                f"{mcp_server.base_url}/health",
                headers=headers,
                timeout=10
            )
            
            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "server": server
            }
        
        except Exception as e:
            logger.error(f"Health check failed for {server}: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "server": server
            }
