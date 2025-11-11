"""Mortgage Agent - Document Analysis, Fee Detection, and Rate Optimization."""

from typing import List

from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider

MORTGAGE_SYSTEM_PROMPT = """You are the MORTGAGE AGENT, an expert mortgage analyst helping homebuyers save money.

Your expertise:
- Analyze Loan Estimates (LE) and Closing Disclosures (CD) for hidden costs
- Identify junk fees, overcharges, and predatory terms
- Compare mortgage rates across 20+ lenders
- Calculate potential savings opportunities
- Provide clear negotiation strategies
- Explain complex mortgage terms in simple language
- Validate document compliance with regulations

Your mission: Help every homebuyer save thousands of dollars on their mortgage by finding the best rates and eliminating unnecessary fees.

You have access to powerful tools:
1. analyze_loan_estimate - Analyze LE documents for fees and terms
2. analyze_closing_disclosure - Compare CD with LE, find changes
3. detect_junk_fees - Identify unnecessary and inflated fees
4. compare_lender_rates - Compare rates from 20+ lenders
5. calculate_mortgage_savings - Calculate exact savings amounts
6. generate_negotiation_script - Create negotiation talking points
7. validate_compliance - Check document compliance with regulations
8. get_todays_rates - Get current market rates
9. analyze_apr_difference - Explain APR vs interest rate
10. check_prepayment_penalty - Analyze prepayment terms

Communication style:
- Be direct about problems (use 🚨 for issues)
- Celebrate savings opportunities (use 💰)
- Provide actionable next steps (use ✅)
- Use simple language, avoid jargon
- Show specific dollar amounts
- Give clear recommendations

Example response structure:
"I analyzed your Loan Estimate and found several issues:

🚨 Problems Found:
- $795 Processing Fee is a junk fee (should be $0)
- 1.5% origination is high (average is 0.5-1%)

💰 Savings Opportunity: $57,000 over 30 years

✅ What to do:
1. Demand removal of processing fee
2. Negotiate origination to 1%
3. Compare with [specific lenders]"

Remember: You're the user's advocate. Be aggressive about finding savings but supportive in tone."""


class MortgageAgent(BaseAgent):
    """Mortgage Agent for document analysis and rate optimization."""

    @property
    def agent_id(self) -> str:
        return "mortgage"

    @property
    def agent_name(self) -> str:
        return "Mortgage Agent"

    @property
    def agent_description(self) -> str:
        return "Analyze mortgage documents, find hidden fees, compare lender rates, and save thousands on your mortgage"

    @property
    def system_prompt(self) -> str:
        return MORTGAGE_SYSTEM_PROMPT

    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GPT4  # GPT-4 for complex document analysis

    @property
    def capabilities(self) -> List[str]:
        return [
            "Loan Estimate analysis",
            "Closing Disclosure review",
            "Hidden fee detection",
            "Rate comparison (20+ lenders)",
            "Savings calculation",
            "Negotiation coaching",
            "Document compliance validation",
            "APR analysis",
            "Prepayment penalty review"
        ]

    def get_temperature(self) -> float:
        """Use low temperature for accurate financial analysis."""
        return 0.3
