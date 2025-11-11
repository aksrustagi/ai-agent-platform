"""Initialize and register all tools for the agent platform."""

from backend.integrations.tool_registry import get_tool_registry
from backend.tools.common_tools import register_common_tools
from backend.tools.content_tools import register_content_tools
from backend.tools.growth_tools import register_growth_tools
from backend.tools.marketing_tools import register_marketing_tools
from backend.tools.mls_tools import register_mls_tools
from backend.tools.mortgage_tools import register_mortgage_tools
from backend.tools.outreach_tools import register_outreach_tools
from backend.tools.transaction_tools import register_transaction_tools
from backend.tools.vendor_tools import register_vendor_tools
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def initialize_all_tools() -> None:
    """
    Initialize and register all tools in the global registry.
    This should be called during application startup.
    """
    logger.info("Initializing all tools...")
    
    registry = get_tool_registry()
    
    # Register common tools available to all agents
    all_agents = ["growth", "outreach", "vendor", "mls", "transaction", "content", "marketing", "mortgage"]
    register_common_tools(registry, agents=all_agents)
    
    # Register agent-specific tools
    logger.info("Registering agent-specific tools...")
    register_growth_tools(registry)
    register_outreach_tools(registry)
    register_mls_tools(registry)
    register_vendor_tools(registry)
    register_transaction_tools(registry)
    register_content_tools(registry)
    register_marketing_tools(registry)
    register_mortgage_tools(registry)
    
    # Log summary
    total_tools = len(registry.list_all_tools())
    categories = registry.list_categories()
    
    logger.info(
        f"Tool initialization complete: {total_tools} tools registered across {len(categories)} categories",
        categories=categories
    )
    
    # Log tools per agent
    for agent_id in all_agents:
        agent_tools = registry.list_agent_tools(agent_id)
        logger.info(f"Agent '{agent_id}' has access to {len(agent_tools)} tools", tools=agent_tools)
