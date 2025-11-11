"""Agent Coordinator for intelligent routing of user queries."""

from typing import Dict, Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.content_agent import ContentAgent
from backend.agents.growth_agent import GrowthAgent
from backend.agents.marketing_agent import MarketingAgent
from backend.agents.mls_agent import MLSAgent
from backend.agents.mortgage_agent import MortgageAgent
from backend.agents.outreach_agent import OutreachAgent
from backend.agents.transaction_agent import TransactionAgent
from backend.agents.vendor_agent import VendorAgent
from backend.config import Settings
from backend.memory.memory_manager import MemoryManager
from backend.models.requests import AgentType
from backend.services.llm_service import LLMProvider, LLMService
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AgentCoordinator:
    """
    Coordinates routing of user messages to appropriate agents.
    """
    
    def __init__(
        self,
        settings: Settings,
        llm_service: LLMService,
        memory_manager: MemoryManager
    ) -> None:
        """
        Initialize agent coordinator.
        
        Args:
            settings: Application settings
            llm_service: LLM service instance
            memory_manager: Memory manager instance
        """
        self.settings = settings
        self.llm_service = llm_service
        self.memory_manager = memory_manager
        
        # Initialize all agents
        self.agents: Dict[str, BaseAgent] = {
            "growth": GrowthAgent(settings, llm_service, memory_manager),
            "outreach": OutreachAgent(settings, llm_service, memory_manager),
            "vendor": VendorAgent(settings, llm_service, memory_manager),
            "mls": MLSAgent(settings, llm_service, memory_manager),
            "transaction": TransactionAgent(settings, llm_service, memory_manager),
            "content": ContentAgent(settings, llm_service, memory_manager),
            "marketing": MarketingAgent(settings, llm_service, memory_manager),
            "mortgage": MortgageAgent(settings, llm_service, memory_manager),
        }
        
        logger.info(f"Agent coordinator initialized with {len(self.agents)} agents")
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        Get agent by type.
        
        Args:
            agent_type: Agent type identifier
        
        Returns:
            Agent instance or None
        """
        return self.agents.get(agent_type)
    
    def list_agents(self) -> Dict[str, BaseAgent]:
        """Get all available agents."""
        return self.agents
    
    async def route_message(
        self,
        user_id: str,
        message: str,
        agent_type: Optional[str] = None,
        conversation_id: Optional[str] = None,
        include_memory: bool = True
    ) -> Dict[str, any]:
        """
        Route a message to the appropriate agent.
        
        Args:
            user_id: User identifier
            message: User message
            agent_type: Optional explicit agent type
            conversation_id: Optional conversation ID
            include_memory: Whether to include memory context
        
        Returns:
            Agent response
        """
        # Determine which agent to use
        if agent_type and agent_type != "auto":
            selected_agent_id = agent_type
            logger.info(f"Using explicitly specified agent: {selected_agent_id}")
        else:
            selected_agent_id = await self._determine_agent(message)
            logger.info(f"Routed message to agent: {selected_agent_id}")
        
        # Get the agent
        agent = self.get_agent(selected_agent_id)
        if not agent:
            logger.error(f"Agent not found: {selected_agent_id}")
            raise ValueError(f"Agent not found: {selected_agent_id}")
        
        # Process message with the agent
        response = await agent.process_message(
            user_id=user_id,
            message=message,
            conversation_id=conversation_id,
            include_memory=include_memory
        )
        
        return response
    
    async def _determine_agent(self, message: str) -> str:
        """
        Determine which agent should handle the message using keyword matching and LLM classification.
        
        Args:
            message: User message
        
        Returns:
            Agent ID
        """
        message_lower = message.lower()
        
        # Keyword-based routing (fast path)
        routing_keywords = {
            "growth": ["goal", "budget", "performance", "revenue", "kpi", "metric", "target", "progress", "analytics"],
            "outreach": ["lead", "contact", "follow up", "email", "sms", "campaign", "nurture", "call", "reach out"],
            "vendor": ["vendor", "inspector", "photographer", "stager", "contractor", "quote", "schedule", "repair"],
            "mls": ["property", "listing", "search", "mls", "cma", "market", "home", "house", "buyer"],
            "transaction": ["contract", "transaction", "closing", "deal", "offer", "purchase agreement", "escrow"],
            "content": ["content", "social media", "post", "blog", "write", "create", "instagram", "facebook"],
            "marketing": ["ads", "advertising", "facebook ads", "google ads", "marketing", "roi", "lead gen"],
        }
        
        # Score each agent based on keyword matches
        scores = {agent_id: 0 for agent_id in routing_keywords.keys()}
        
        for agent_id, keywords in routing_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[agent_id] += 1
        
        # Get agent with highest score
        max_score = max(scores.values())
        
        if max_score > 0:
            # Return agent with highest score
            for agent_id, score in scores.items():
                if score == max_score:
                    return agent_id
        
        # Default to growth agent for general queries
        logger.info("No clear keyword match, defaulting to growth agent")
        return "growth"
    
    async def _llm_classify_message(self, message: str) -> str:
        """
        Use LLM to classify which agent should handle the message (fallback method).
        
        Args:
            message: User message
        
        Returns:
            Agent ID
        """
        classification_prompt = f"""Classify which agent should handle this real estate professional's message.

Available agents:
- growth: Goals, KPIs, budgets, performance analytics
- outreach: Lead nurturing, follow-ups, campaigns, email/SMS
- vendor: Vendor coordination, quotes, scheduling, contractors
- mls: Property search, listings, market analysis, CMAs
- transaction: Contracts, deals, closings, transaction management
- content: Content creation, social media, blog posts
- marketing: Ads, lead generation, marketing ROI

Message: "{message}"

Respond with ONLY the agent ID (e.g., "growth", "outreach", etc.)"""
        
        try:
            response = await self.llm_service.generate(
                provider=LLMProvider.GPT4,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            agent_id = response["content"].strip().lower()
            
            if agent_id in self.agents:
                return agent_id
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
        
        # Default fallback
        return "growth"
