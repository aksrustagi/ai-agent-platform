"""MLS & Property Search Agent."""

from typing import List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

MLS_SYSTEM_PROMPT = """You are the MLS AGENT. You search properties via RealEstateAPI.com, provide CMAs, analyze market data, and help find perfect properties for buyers."""

class MLSAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "mls"
    
    @property
    def agent_name(self) -> str:
        return "MLS Agent"
    
    @property
    def agent_description(self) -> str:
        return "Property search, CMAs, and market analysis"
    
    @property
    def system_prompt(self) -> str:
        return MLS_SYSTEM_PROMPT
    
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GPT4
    
    @property
    def capabilities(self) -> List[str]:
        return ["Property search", "Market analysis", "CMA generation"]
