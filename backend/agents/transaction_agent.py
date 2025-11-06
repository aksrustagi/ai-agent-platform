"""Transaction Management Agent."""
from typing import List
from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

TRANSACTION_SYSTEM_PROMPT = """You are the TRANSACTION AGENT. You manage contracts, forms, transaction timelines, and ensure smooth closings."""

class TransactionAgent(BaseAgent):
    @property
    def agent_id(self) -> str:
        return "transaction"
    @property
    def agent_name(self) -> str:
        return "Transaction Agent"
    @property
    def agent_description(self) -> str:
        return "Contract management and transaction coordination"
    @property
    def system_prompt(self) -> str:
        return TRANSACTION_SYSTEM_PROMPT
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.CLAUDE
    @property
    def capabilities(self) -> List[str]:
        return ["Contract management", "Transaction tracking", "Closing coordination"]
