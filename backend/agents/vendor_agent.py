"""Vendor Coordination Agent - Fast vendor discovery and coordination."""

from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

VENDOR_SYSTEM_PROMPT = """You are the VENDOR COORDINATION AGENT. You're lightning-fast, detail-oriented with scheduling, cost-conscious, and highly organized. You find qualified vendors (inspectors, photographers, stagers, contractors), get quotes, compare pricing, negotiate rates, schedule services, and track vendor performance. Always get 2-3 options, check ratings 4.5+, verify licenses/insurance, and recommend the best option with clear reasoning."""


class VendorAgent(BaseAgent):
    """Vendor Coordination Agent using Groq for speed."""
    
    @property
    def agent_id(self) -> str:
        return "vendor"
    
    @property
    def agent_name(self) -> str:
        return "Vendor Agent"
    
    @property
    def agent_description(self) -> str:
        return "Vendor discovery, quote management, scheduling, and coordination"
    
    @property
    def system_prompt(self) -> str:
        return VENDOR_SYSTEM_PROMPT
    
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GROQ
    
    @property
    def capabilities(self) -> List[str]:
        return ["Vendor search", "Quote comparison", "Service scheduling", "Performance tracking"]
    
    def get_temperature(self) -> float:
        return 0.3  # Low temperature for consistent, fast responses
