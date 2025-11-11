"""Tests for the MCP tool system."""

import pytest

from backend.integrations.mcp_client import MCPClient, Tool
from backend.integrations.tool_registry import ToolRegistry, reset_tool_registry
from backend.tools.tool_initialization import initialize_all_tools


@pytest.fixture
def mcp_client():
    """Create a fresh MCP client for testing."""
    return MCPClient()


@pytest.fixture
def tool_registry():
    """Create a fresh tool registry for testing."""
    reset_tool_registry()
    from backend.integrations.tool_registry import get_tool_registry
    return get_tool_registry()


class TestMCPClient:
    """Test the MCP client."""
    
    def test_register_tool(self, mcp_client):
        """Test tool registration."""
        def my_tool(param1: str) -> str:
            return f"Result: {param1}"
        
        mcp_client.register_tool(
            name="my_tool",
            description="Test tool",
            function=my_tool,
            parameters={
                "type": "object",
                "properties": {"param1": {"type": "string"}},
                "required": ["param1"]
            }
        )
        
        assert "my_tool" in mcp_client.tools
        tool = mcp_client.get_tool("my_tool")
        assert tool is not None
        assert tool.name == "my_tool"
    
    @pytest.mark.asyncio
    async def test_execute_tool(self, mcp_client):
        """Test tool execution."""
        async def async_tool(value: int) -> int:
            return value * 2
        
        mcp_client.register_tool(
            name="async_tool",
            description="Async test tool",
            function=async_tool,
            parameters={
                "type": "object",
                "properties": {"value": {"type": "integer"}},
                "required": ["value"]
            }
        )
        
        result = await mcp_client.execute_tool("async_tool", {"value": 21})
        assert result["success"]
        assert result["result"] == 42
    
    def test_get_tools_schema(self, mcp_client):
        """Test getting tool schemas."""
        def tool1():
            pass
        
        def tool2():
            pass
        
        mcp_client.register_tool(
            name="tool1",
            description="Tool 1",
            function=tool1,
            parameters={"type": "object", "properties": {}},
            category="cat1"
        )
        
        mcp_client.register_tool(
            name="tool2",
            description="Tool 2",
            function=tool2,
            parameters={"type": "object", "properties": {}},
            category="cat2"
        )
        
        # Get all tools
        all_schemas = mcp_client.get_tools_schema()
        assert len(all_schemas) == 2
        
        # Get by category
        cat1_schemas = mcp_client.get_tools_schema(category="cat1")
        assert len(cat1_schemas) == 1
        assert cat1_schemas[0]["name"] == "tool1"


class TestToolRegistry:
    """Test the tool registry."""
    
    def test_register_and_assign_tool(self, tool_registry):
        """Test registering a tool and assigning to agents."""
        async def test_tool(param: str) -> str:
            return param
        
        tool_registry.register_tool(
            name="test_tool",
            description="Test",
            function=test_tool,
            parameters={
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"]
            },
            agents=["agent1", "agent2"]
        )
        
        # Check tool is registered
        assert "test_tool" in tool_registry.list_all_tools()
        
        # Check agents have access
        agent1_tools = tool_registry.list_agent_tools("agent1")
        assert "test_tool" in agent1_tools
        
        agent2_tools = tool_registry.list_agent_tools("agent2")
        assert "test_tool" in agent2_tools
    
    @pytest.mark.asyncio
    async def test_execute_with_access_control(self, tool_registry):
        """Test tool execution with agent access control."""
        async def restricted_tool() -> str:
            return "secret"
        
        tool_registry.register_tool(
            name="restricted_tool",
            description="Restricted",
            function=restricted_tool,
            parameters={"type": "object", "properties": {}},
            agents=["agent1"]
        )
        
        # Agent1 can execute
        result1 = await tool_registry.execute_tool("restricted_tool", {}, agent_id="agent1")
        assert result1["success"]
        assert result1["result"] == "secret"
        
        # Agent2 cannot execute
        result2 = await tool_registry.execute_tool("restricted_tool", {}, agent_id="agent2")
        assert not result2["success"]
        assert "does not have access" in result2["error"]
    
    def test_get_tools_for_agent(self, tool_registry):
        """Test getting tools for a specific agent."""
        def tool_a():
            pass
        
        def tool_b():
            pass
        
        tool_registry.register_tool(
            name="tool_a",
            description="Tool A",
            function=tool_a,
            parameters={"type": "object", "properties": {}},
            agents=["agent1"]
        )
        
        tool_registry.register_tool(
            name="tool_b",
            description="Tool B",
            function=tool_b,
            parameters={"type": "object", "properties": {}},
            agents=["agent1", "agent2"]
        )
        
        # Agent1 should have both tools
        agent1_schemas = tool_registry.get_tools_for_agent("agent1")
        assert len(agent1_schemas) == 2
        
        # Agent2 should have only tool_b
        agent2_schemas = tool_registry.get_tools_for_agent("agent2")
        assert len(agent2_schemas) == 1
        assert agent2_schemas[0]["name"] == "tool_b"


class TestToolInitialization:
    """Test tool initialization."""
    
    def test_initialize_all_tools(self, tool_registry):
        """Test initializing all tools."""
        initialize_all_tools()
        
        # Check that tools are registered
        all_tools = tool_registry.list_all_tools()
        assert len(all_tools) > 0
        
        # Check categories exist
        categories = tool_registry.list_categories()
        assert "utility" in categories
        assert "outreach" in categories
        assert "mls" in categories
        
        # Check specific tools
        assert "get_current_date_time" in all_tools
        assert "search_leads" in all_tools
        assert "search_properties" in all_tools
    
    def test_agents_have_tools(self, tool_registry):
        """Test that agents have appropriate tools after initialization."""
        initialize_all_tools()
        
        # Outreach agent should have outreach tools
        outreach_tools = tool_registry.list_agent_tools("outreach")
        assert "search_leads" in outreach_tools
        assert "send_email" in outreach_tools
        
        # MLS agent should have MLS tools
        mls_tools = tool_registry.list_agent_tools("mls")
        assert "search_properties" in mls_tools
        assert "generate_cma" in mls_tools
        
        # All agents should have common tools
        for agent_id in ["growth", "outreach", "mls"]:
            agent_tools = tool_registry.list_agent_tools(agent_id)
            assert "get_current_date_time" in agent_tools
            assert "calculate" in agent_tools


@pytest.mark.asyncio
async def test_tool_execution_flow():
    """Test complete tool execution flow."""
    reset_tool_registry()
    initialize_all_tools()
    
    from backend.integrations.tool_registry import get_tool_registry
    registry = get_tool_registry()
    
    # Test calculate tool
    result = await registry.execute_tool(
        "calculate",
        {"expression": "10 + 5 * 2"},
        agent_id="growth"
    )
    assert result["success"]
    assert result["result"]["result"] == 20
    
    # Test get_current_date_time
    result = await registry.execute_tool(
        "get_current_date_time",
        {},
        agent_id="outreach"
    )
    assert result["success"]
    assert "date" in result["result"]
    assert "time" in result["result"]
