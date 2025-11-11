"""Common tools available to multiple agents."""

from datetime import datetime
from typing import Any, Dict, Optional

from backend.integrations.tool_registry import ToolRegistry
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def get_current_date_time() -> Dict[str, Any]:
    """Get the current date and time."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "datetime": now.isoformat(),
        "day_of_week": now.strftime("%A"),
        "timezone": "UTC"
    }


async def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely calculate a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate
    
    Returns:
        Calculation result
    """
    try:
        # Basic safety: only allow numbers and operators
        allowed_chars = set("0123456789+-*/()%. ")
        if not all(c in allowed_chars for c in expression):
            return {
                "success": False,
                "error": "Expression contains invalid characters"
            }
        
        result = eval(expression)
        return {
            "success": True,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def search_memory(
    user_id: str,
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search user's memory for relevant information.
    
    Args:
        user_id: User identifier
        query: Search query
        limit: Maximum results
    
    Returns:
        Search results
    """
    # TODO: Integrate with actual memory manager
    logger.info(f"Searching memory for user {user_id}", query=query)
    
    return {
        "success": True,
        "query": query,
        "results": [],
        "count": 0
    }


async def store_fact(
    user_id: str,
    fact: str,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Store an important fact in user's memory.
    
    Args:
        user_id: User identifier
        fact: Fact to store
        category: Optional category
    
    Returns:
        Storage confirmation
    """
    # TODO: Integrate with actual memory manager
    logger.info(f"Storing fact for user {user_id}", category=category)
    
    return {
        "success": True,
        "fact": fact,
        "category": category,
        "stored_at": datetime.now().isoformat()
    }


def register_common_tools(registry: ToolRegistry, agents: Optional[list] = None) -> None:
    """
    Register common tools available to multiple agents.
    
    Args:
        registry: Tool registry instance
        agents: Optional list of agent IDs. If None, available to all agents.
    """
    # Get current date/time tool
    registry.register_tool(
        name="get_current_date_time",
        description="Get the current date and time",
        function=get_current_date_time,
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        },
        category="utility",
        agents=agents
    )
    
    # Calculator tool
    registry.register_tool(
        name="calculate",
        description="Calculate a mathematical expression",
        function=calculate,
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '10 + 5 * 2')"
                }
            },
            "required": ["expression"]
        },
        category="utility",
        agents=agents
    )
    
    # Memory search tool
    registry.register_tool(
        name="search_memory",
        description="Search user's memory for relevant information",
        function=search_memory,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results"
                }
            },
            "required": ["user_id", "query"]
        },
        category="memory",
        agents=agents
    )
    
    # Store fact tool
    registry.register_tool(
        name="store_fact",
        description="Store an important fact in user's memory",
        function=store_fact,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "User identifier"
                },
                "fact": {
                    "type": "string",
                    "description": "Fact to store"
                },
                "category": {
                    "type": "string",
                    "description": "Optional category for the fact"
                }
            },
            "required": ["user_id", "fact"]
        },
        category="memory",
        agents=agents
    )
    
    logger.info(f"Registered {4} common tools")
