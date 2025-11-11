# Quick Start: Adding Tools to Agents

## Overview

This guide shows you how to add new tools to your agents in 5 minutes.

## The 3-Step Process

### Step 1: Create Your Tool Function

Create a new file or add to existing file in `backend/tools/`:

```python
# backend/tools/my_tools.py
from typing import Dict, Any
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def my_awesome_tool(
    param1: str,
    param2: int,
    optional_param: str = "default"
) -> Dict[str, Any]:
    """
    Short description of what your tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        optional_param: Description of optional parameter
    
    Returns:
        Dictionary with success status and result
    """
    logger.info(f"Executing my_awesome_tool with {param1}")
    
    # Your tool logic here
    result = do_something(param1, param2)
    
    return {
        "success": True,
        "result": result,
        "message": "Tool executed successfully"
    }
```

**Key Points**:
- Use async functions for I/O operations
- Always return a dictionary with `success` key
- Include type hints for all parameters
- Write a clear docstring
- Log important actions

### Step 2: Register Your Tool

Add a registration function in the same file:

```python
# backend/tools/my_tools.py (continued)
from backend.integrations.tool_registry import ToolRegistry

def register_my_tools(registry: ToolRegistry) -> None:
    """Register my custom tools."""
    
    # List of agents that should have access to this tool
    agents = ["growth", "outreach"]  # or ["*"] for all agents
    
    registry.register_tool(
        name="my_awesome_tool",
        description="Short description for the LLM to understand when to use this tool",
        function=my_awesome_tool,
        parameters={
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "What param1 is for"
                },
                "param2": {
                    "type": "integer",
                    "description": "What param2 is for"
                },
                "optional_param": {
                    "type": "string",
                    "description": "Optional parameter"
                }
            },
            "required": ["param1", "param2"]  # optional_param is optional
        },
        category="my_category",
        agents=agents,
        requires_confirmation=False  # Set True for destructive actions
    )
    
    logger.info("Registered my custom tools")
```

**Parameter Schema Types**:
- `"string"`: Text
- `"integer"`: Whole numbers
- `"number"`: Decimals
- `"boolean"`: True/False
- `"array"`: Lists
- `"object"`: Nested dictionaries

### Step 3: Add to Initialization

Update `backend/tools/tool_initialization.py`:

```python
# Add import at top
from backend.tools.my_tools import register_my_tools

# Add to initialize_all_tools() function
def initialize_all_tools() -> None:
    logger.info("Initializing all tools...")
    
    registry = get_tool_registry()
    
    # Existing registrations...
    register_common_tools(registry, agents=all_agents)
    register_outreach_tools(registry)
    register_mls_tools(registry)
    
    # Add your registration
    register_my_tools(registry)  # ← Add this line
    
    # Rest of function...
```

**That's it!** Your tool is now available to the specified agents.

## Quick Examples

### Example 1: Simple Calculation Tool

```python
async def calculate_roi(
    investment: float,
    return_amount: float
) -> Dict[str, Any]:
    """Calculate return on investment."""
    roi = ((return_amount - investment) / investment) * 100
    
    return {
        "success": True,
        "roi_percentage": round(roi, 2),
        "profit": return_amount - investment
    }

# Register
registry.register_tool(
    name="calculate_roi",
    description="Calculate ROI percentage from investment and return amounts",
    function=calculate_roi,
    parameters={
        "type": "object",
        "properties": {
            "investment": {"type": "number", "description": "Initial investment amount"},
            "return_amount": {"type": "number", "description": "Total return amount"}
        },
        "required": ["investment", "return_amount"]
    },
    agents=["growth", "marketing"]
)
```

### Example 2: External API Tool

```python
import httpx

async def get_weather(
    location: str
) -> Dict[str, Any]:
    """Get current weather for a location."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/v1/current",
            params={"location": location}
        )
        data = response.json()
    
    return {
        "success": True,
        "location": location,
        "temperature": data["temp"],
        "conditions": data["conditions"]
    }

# Register
registry.register_tool(
    name="get_weather",
    description="Get current weather conditions for a location",
    function=get_weather,
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name or zip code"}
        },
        "required": ["location"]
    },
    agents=["*"]  # Available to all agents
)
```

### Example 3: Database Query Tool

```python
async def get_user_stats(
    user_id: str,
    metric: str
) -> Dict[str, Any]:
    """Get user statistics from database."""
    # Your database query here
    async with get_db_connection() as db:
        stats = await db.query(
            "SELECT * FROM user_stats WHERE user_id = $1 AND metric = $2",
            user_id, metric
        )
    
    return {
        "success": True,
        "user_id": user_id,
        "metric": metric,
        "value": stats[0]["value"] if stats else None
    }

# Register
registry.register_tool(
    name="get_user_stats",
    description="Retrieve user statistics from the database",
    function=get_user_stats,
    parameters={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User identifier"},
            "metric": {
                "type": "string",
                "enum": ["revenue", "leads", "conversions"],
                "description": "Metric to retrieve"
            }
        },
        "required": ["user_id", "metric"]
    },
    agents=["growth"]
)
```

## Advanced Features

### Auto-Registration from Function

If you have good type hints and docstrings, you can auto-register:

```python
async def my_tool(param1: str, param2: int) -> Dict[str, Any]:
    """Tool description."""
    return {"success": True, "result": "done"}

# Auto-register (parameters extracted from type hints)
registry.register_tool_from_function(
    function=my_tool,
    category="my_category",
    agents=["growth"]
)
```

### Tool Confirmation

For tools that perform destructive actions:

```python
registry.register_tool(
    name="delete_lead",
    description="Permanently delete a lead",
    function=delete_lead,
    parameters={...},
    agents=["outreach"],
    requires_confirmation=True  # UI should ask user before executing
)
```

### Tool Categories

Organize tools by category:

```python
# Register multiple tools in same category
for tool_func in [tool1, tool2, tool3]:
    registry.register_tool(
        ...,
        category="crm_operations"
    )

# Later, get all tools in category
crm_tools = registry.get_all_tools(category="crm_operations")
```

### Dynamic Tool Assignment

Assign tools to agents at runtime:

```python
# Assign existing tool to new agent
registry.assign_tool_to_agent("my_awesome_tool", "vendor")

# Remove tool from agent
registry.unassign_tool_from_agent("my_awesome_tool", "vendor")
```

## Testing Your Tool

### Unit Test

```python
# backend/tests/test_my_tools.py
import pytest
from backend.tools.my_tools import my_awesome_tool

@pytest.mark.asyncio
async def test_my_awesome_tool():
    result = await my_awesome_tool("test", 42)
    assert result["success"]
    assert "result" in result
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_tool_via_registry():
    from backend.integrations.tool_registry import get_tool_registry
    from backend.tools.tool_initialization import initialize_all_tools
    
    initialize_all_tools()
    registry = get_tool_registry()
    
    result = await registry.execute_tool(
        "my_awesome_tool",
        {"param1": "test", "param2": 42},
        agent_id="growth"
    )
    
    assert result["success"]
```

### Manual Test

```bash
cd ai-agent-platform

python -c "
import asyncio
from backend.tools.my_tools import my_awesome_tool

async def test():
    result = await my_awesome_tool('test', 42)
    print(result)

asyncio.run(test())
"
```

## Best Practices

### ✅ DO

- **Use type hints** on all parameters
- **Return dictionaries** with `success` key
- **Log important actions** for debugging
- **Handle errors gracefully** and return error info
- **Write clear descriptions** for the LLM
- **Use async** for I/O operations
- **Keep tools focused** (one responsibility)

### ❌ DON'T

- Don't raise exceptions (return error info instead)
- Don't perform destructive actions without confirmation flag
- Don't make tools too complex (split into multiple tools)
- Don't forget to register in initialization
- Don't hardcode agent-specific logic in tools

## Error Handling

```python
async def my_tool(param: str) -> Dict[str, Any]:
    """My tool with error handling."""
    try:
        result = await risky_operation(param)
        return {
            "success": True,
            "result": result
        }
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        return {
            "success": False,
            "error": f"Invalid parameter: {str(e)}",
            "error_type": "ValueError"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Operation failed: {str(e)}",
            "error_type": "UnexpectedError"
        }
```

## Checking Tool Availability

### List All Tools

```python
from backend.integrations.tool_registry import get_tool_registry

registry = get_tool_registry()

# List all tool names
all_tools = registry.list_all_tools()
print(f"Available tools: {all_tools}")

# List by category
utility_tools = registry.list_all_tools(category="utility")
```

### Check Agent Tools

```python
# List tools for specific agent
outreach_tools = registry.list_agent_tools("outreach")
print(f"Outreach agent has {len(outreach_tools)} tools")

# Get full schemas
tool_schemas = registry.get_tools_for_agent("outreach")
for schema in tool_schemas:
    print(f"- {schema['name']}: {schema['description']}")
```

## Common Patterns

### Tool that Calls Another Tool

```python
async def complex_task(user_id: str) -> Dict[str, Any]:
    """Complex task using multiple tools."""
    from backend.integrations.tool_registry import get_tool_registry
    registry = get_tool_registry()
    
    # Call first tool
    result1 = await registry.execute_tool("tool1", {...})
    
    # Use result to call second tool
    result2 = await registry.execute_tool("tool2", {
        "data": result1["result"]
    })
    
    return {
        "success": True,
        "final_result": result2["result"]
    }
```

### Tool with Progress Updates

```python
async def long_running_task(items: list) -> Dict[str, Any]:
    """Process many items."""
    results = []
    
    for i, item in enumerate(items):
        logger.info(f"Processing item {i+1}/{len(items)}")
        result = await process_item(item)
        results.append(result)
    
    return {
        "success": True,
        "processed": len(results),
        "results": results
    }
```

## Troubleshooting

### Tool Not Available to Agent

```python
# Check if tool is registered
registry = get_tool_registry()
if "my_tool" not in registry.list_all_tools():
    print("Tool not registered!")

# Check if agent has access
if "my_tool" not in registry.list_agent_tools("growth"):
    print("Agent doesn't have access!")
    # Assign it
    registry.assign_tool_to_agent("my_tool", "growth")
```

### Tool Execution Fails

```python
# Check tool execution directly
result = await registry.execute_tool("my_tool", {...}, agent_id="growth")

if not result["success"]:
    print(f"Error: {result['error']}")
    # Check logs for details
```

## Next Steps

1. **Read** `AGENTIC_ARCHITECTURE.md` for deep dive
2. **Study** existing tools in `backend/tools/`
3. **Create** your first tool following this guide
4. **Test** your tool thoroughly
5. **Deploy** and monitor usage

Happy tool building! 🛠️
