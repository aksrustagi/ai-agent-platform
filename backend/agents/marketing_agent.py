"""Marketing & Advertising Agent."""
from typing import List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

MARKETING_SYSTEM_PROMPT = """You are the MARKETING AGENT. You manage ads, lead purchasing, ROI optimization, and marketing strategy."""

class MarketingAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "marketing"
    @property
    def agent_name(self) -> str:
        return "Marketing Agent"
    @property
    def agent_description(self) -> str:
        return "Advertising, lead generation, and ROI optimization"
    @property
    def system_prompt(self) -> str:
        return MARKETING_SYSTEM_PROMPT
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GPT4
    @property
    def capabilities(self) -> List[str]:
        return ["Ad campaign management", "Lead purchasing", "ROI analysis"]
