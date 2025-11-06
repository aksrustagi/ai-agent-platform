"""Content Creation Agent."""
from typing import List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

CONTENT_SYSTEM_PROMPT = """You are the CONTENT AGENT. You create engaging content for social media, blogs, emails, and property listings."""

class ContentAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "content"
    @property
    def agent_name(self) -> str:
        return "Content Agent"
    @property
    def agent_description(self) -> str:
        return "Content creation and social media management"
    @property
    def system_prompt(self) -> str:
        return CONTENT_SYSTEM_PROMPT
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.CLAUDE
    @property
    def capabilities(self) -> List[str]:
        return ["Content writing", "Social media posting", "Email templates"]
    def get_temperature(self) -> float:
        return 0.8  # Higher temperature for creative content
