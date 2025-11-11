# Agentic Architecture with MCP and Tool Calling

## Overview

The AI Agent Platform has been transformed from a simple chat completion interface to a fully agentic system with proper MCP (Model Context Protocol) integration and multi-turn tool calling capabilities.

## Key Changes

### 1. Enhanced MCP Client (`backend/integrations/mcp_client.py`)

The MCP client now provides:
- **Tool Class**: Encapsulates tool metadata, execution logic, and schema generation
- **Proper Tool Registration**: Register tools with name, description, function, parameters, and category
- **Auto-detection**: Register tools from functions with type hints and docstrings
- **Tool Execution**: Async execution with error handling
- **Schema Management**: Generate LLM-compatible tool schemas (OpenAI and Anthropic formats)
- **Category Support**: Organize tools by category (utility, memory, outreach, mls, etc.)

### 2. Tool Registry (`backend/integrations/tool_registry.py`)

A centralized registry that:
- **Manages All Tools**: Single source of truth for all available tools
- **Agent-Tool Mapping**: Controls which agents have access to which tools
- **Access Control**: Validates tool access per agent
- **Tool Discovery**: Agents can query available tools dynamically
- **Global Instance**: Singleton pattern for easy access across the application

### 3. Agentic Loop in BaseAgent (`backend/agents/base_agent.py`)

The core improvement - agents now:
- **Multi-turn Conversations**: Can call tools, process results, and call more tools
- **Iterative Problem Solving**: Loop until final answer or max iterations
- **Tool Call History**: Track all tool calls and results
- **Conversation Context**: Maintain full context including tool results
- **Token Tracking**: Accumulate usage across all iterations

**Before (Simple Chat Completion):**
```
User Message → LLM → Response (with optional single tool call)
```

**After (Agentic Loop):**
```
User Message → LLM → Tool Calls → Execute Tools → 
  → LLM (with results) → More Tool Calls or Final Answer → 
  → Repeat until Final Answer or Max Iterations
```

### 4. Concrete Tool Implementations

Created organized tool modules:

**Common Tools** (`backend/tools/common_tools.py`):
- `get_current_date_time`: Get current date/time
- `calculate`: Evaluate mathematical expressions
- `search_memory`: Search user's memory
- `store_fact`: Store facts in memory

**Outreach Tools** (`backend/tools/outreach_tools.py`):
- `search_leads`: Find leads by criteria
- `send_email`: Send personalized emails
- `send_sms`: Send SMS messages
- `create_campaign`: Create nurture campaigns
- `get_lead_engagement`: Get engagement metrics

**MLS Tools** (`backend/tools/mls_tools.py`):
- `search_properties`: Search real estate listings
- `get_property_details`: Get property information
- `generate_cma`: Generate Comparative Market Analysis
- `get_market_statistics`: Get market stats

### 5. Enhanced LLM Service

Updated tool calling support:
- **Claude**: Properly parse `tool_use` content blocks
- **GPT-4**: Standard OpenAI tool calling format
- **Unified Interface**: Convert different formats to standard structure

### 6. Tool Initialization

Automatic tool registration at startup:
- All tools registered when app starts
- Agent-tool mappings configured
- Logging of all registered tools
- Per-agent tool inventory

## How It Works

### Agent-Tool Flow

1. **Startup**: `initialize_all_tools()` registers all tools in the registry
2. **User Request**: User sends message to agent
3. **Agent Retrieves Tools**: Agent queries registry for its available tools
4. **LLM Generation**: Agent sends request to LLM with tools schema
5. **Tool Calling**: LLM decides to call tools
6. **Tool Execution**: Agent executes tools via registry
7. **Result Processing**: Results fed back to LLM
8. **Iteration**: Steps 5-7 repeat until final answer
9. **Response**: Final answer returned to user

### Example Agentic Interaction

**User**: "Find leads who haven't been contacted in 30 days and send them a follow-up email"

**Agent Iteration 1**:
- LLM decides to use `search_leads` tool
- Tool returns list of 3 leads

**Agent Iteration 2**:
- LLM analyzes results
- Decides to use `send_email` for each lead
- Calls tool 3 times

**Agent Iteration 3**:
- LLM receives confirmation of 3 emails sent
- Generates final response: "I found 3 leads and sent personalized follow-up emails..."

## Architecture Benefits

### 1. True Agent Behavior
- Agents can reason about what tools to use
- Multi-step problem solving
- Context-aware decision making

### 2. Extensibility
- Easy to add new tools
- Tools can be shared across agents
- Clear separation of concerns

### 3. Maintainability
- Centralized tool management
- Consistent tool interface
- Easy to test tools independently

### 4. Control & Security
- Access control per agent
- Tool confirmation flags
- Execution tracking and logging

### 5. Standards Compliance
- MCP-compatible architecture
- Works with Claude and GPT-4 tool calling
- Easy to extend to other LLMs

## Tool Development Guide

### Creating a New Tool

```python
async def my_tool(param1: str, param2: int) -> Dict[str, Any]:
    """
    Tool description that will be shown to the LLM.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Tool result
    """
    # Tool implementation
    result = do_something(param1, param2)
    return {
        "success": True,
        "result": result
    }
```

### Registering a Tool

```python
from backend.integrations.tool_registry import get_tool_registry

registry = get_tool_registry()

# Manual registration with full control
registry.register_tool(
    name="my_tool",
    description="Do something useful",
    function=my_tool,
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "integer", "description": "..."}
        },
        "required": ["param1", "param2"]
    },
    category="my_category",
    agents=["agent1", "agent2"],
    requires_confirmation=False
)

# Or auto-register from function with type hints
registry.register_tool_from_function(
    function=my_tool,
    category="my_category",
    agents=["agent1", "agent2"]
)
```

### Assigning Tools to Agents

```python
# During registration
registry.register_tool(..., agents=["outreach", "mls"])

# Or dynamically
registry.assign_tool_to_agent("my_tool", "growth")
registry.unassign_tool_from_agent("my_tool", "growth")
```

## Testing Tools

Tools can be tested independently:

```python
import pytest
from backend.tools.outreach_tools import search_leads

@pytest.mark.asyncio
async def test_search_leads():
    result = await search_leads(temperature="hot", limit=5)
    assert result["success"]
    assert len(result["leads"]) <= 5
```

## Configuration

### Max Iterations

Control how many tool-calling iterations an agent can perform:

```python
response = await agent.process_message(
    user_id="user_123",
    message="Find and email hot leads",
    max_iterations=5  # Default is 5
)
```

### Tool Confirmation

Some tools (like sending emails) can require confirmation:

```python
registry.register_tool(
    ...,
    requires_confirmation=True  # Flag for UI to request confirmation
)
```

## Monitoring & Logging

The system logs:
- Tool registrations at startup
- Tool calls during execution
- Tool execution results (success/failure)
- Agentic loop iterations
- Token usage across iterations

Example logs:
```
[INFO] Tool initialization complete: 13 tools registered across 4 categories
[INFO] Agent 'outreach' has access to 9 tools
[INFO] Agentic loop iteration 1/5
[INFO] Executing 2 tool(s)
[INFO] Executing MCP tool: search_leads
[INFO] Tool execution complete: search_leads (success)
```

## Future Enhancements

### Planned Improvements

1. **Composio Integration**: Convert Composio apps to MCP tools
2. **RealEstateAPI Integration**: Real MLS data via tools
3. **Parallel Tool Execution**: Execute independent tools concurrently
4. **Tool Versioning**: Support multiple versions of tools
5. **Tool Marketplace**: Share and discover tools
6. **Streaming Tool Results**: Stream partial results for long-running tools
7. **Tool Caching**: Cache tool results for common queries
8. **Tool Analytics**: Track tool usage and effectiveness

### Integration Ideas

- **Database Tools**: Query user's database
- **CRM Tools**: Integrate with real CRM systems
- **Calendar Tools**: Schedule appointments
- **Document Tools**: Generate and process documents
- **External APIs**: Weather, news, stock prices, etc.

## Migration Guide

### Converting Old Agents

**Before:**
```python
class MyAgent(BaseAgent):
    @property
    def available_tools(self) -> List[Dict[str, Any]]:
        return [{"name": "my_tool", ...}]
    
    async def execute_tool(self, tool_name: str, args: Dict) -> Any:
        if tool_name == "my_tool":
            return await self._my_tool(args)
```

**After:**
```python
# In tool registration (during startup):
registry.register_tool(
    name="my_tool",
    function=my_tool_function,
    agents=["my_agent"],
    ...
)

# Agent is automatically configured!
class MyAgent(BaseAgent):
    # available_tools is inherited from BaseAgent
    # execute_tool is inherited from BaseAgent
    pass
```

## Conclusion

The platform is now a true agentic system where agents can:
- **Think** about what tools to use
- **Act** by calling tools
- **Observe** results
- **Iterate** until solving the user's problem

This architecture provides a solid foundation for building sophisticated AI agents that can handle complex, multi-step tasks autonomously.
