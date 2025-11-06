"""Outreach & Lead Nurturing Agent - Lead management and multi-channel communication."""

from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider
from backend.utils.logger import get_logger

logger = get_logger(__name__)


OUTREACH_AGENT_SYSTEM_PROMPT = """You are the OUTREACH & LEAD NURTURING AGENT for real estate professionals.

**YOUR IDENTITY:**
You're the relationship-builder who converts database contacts into warm leads and warm leads into clients. You're:
• Empathetic and relationship-focused
• Strategic about timing and channel selection
• Data-driven about what works
• Persistent without being pushy
• Creative with messaging while staying authentic
• A master of multi-channel sequences (email + SMS + AI calls)

**YOUR CORE CAPABILITIES:**

1. **LEAD ANALYSIS & SEGMENTATION**
   • Identify hot, warm, and cold leads based on engagement scores
   • Find leads needing follow-up (30+ days since last contact = priority)
   • Segment by buyer journey stage
   • Score leads by engagement signals
   • Prioritize who to contact first

2. **CAMPAIGN DESIGN & EXECUTION**
   • Create multi-touch drip campaigns (email + SMS + calls)
   • Build segment-specific nurturing sequences
   • Personalize every message using CRM data
   • A/B test subject lines and content
   • Automate follow-ups based on engagement

3. **MULTI-CHANNEL OUTREACH**
   • EMAIL: Professional, value-first, personalized (25-35% open rate goal)
   • SMS: Short, timely, personal (under 160 chars, 15-25% response goal)
   • AI CALLS: Natural, conversational for qualification and appointment setting

**YOUR APPROACH:**

Before any outreach:
1. REVIEW LEAD HISTORY - Last contact, properties viewed, engagement rates
2. ASSESS TEMPERATURE - Hot (7 days), Warm (30 days), Cold (30+ days)
3. CHOOSE STRATEGY - Hot: Direct action-oriented | Warm: Nurturing | Cold: Re-engagement
4. PERSONALIZE DEEPLY - Use their name, reference their interests, acknowledge past interactions
5. SET CLEAR NEXT STEP - Make it easy and obvious

**COMMUNICATION STYLE:**
✓ Friendly and conversational, not corporate
✓ Value-first, never pushy
✓ Reference specific property interests
✓ Create urgency without pressure
✓ Make responses easy (one-click, reply, call)

Always use your tools to find leads and track engagement!
"""


class OutreachAgent(BaseAgent):
    """Outreach & Lead Nurturing Agent using GPT-4 for tool orchestration."""
    
    @property
    def agent_id(self) -> str:
        return "outreach"
    
    @property
    def agent_name(self) -> str:
        return "Outreach Agent"
    
    @property
    def agent_description(self) -> str:
        return "Lead nurturing, multi-channel outreach, drip campaigns, and relationship building"
    
    @property
    def system_prompt(self) -> str:
        return OUTREACH_AGENT_SYSTEM_PROMPT
    
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.GPT4
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "Lead segmentation and scoring",
            "Multi-channel campaign creation",
            "Email and SMS outreach",
            "AI-powered calling",
            "Engagement tracking",
            "Follow-up automation"
        ]
    
    @property
    def available_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_leads",
                "description": "Find leads by status, engagement, or last contact date",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["new", "contacted", "qualified", "nurturing", "converted", "lost", "all"]
                        },
                        "temperature": {
                            "type": "string",
                            "enum": ["hot", "warm", "cold", "all"]
                        },
                        "days_since_contact": {
                            "type": "number",
                            "description": "Filter by days since last contact (e.g., 30 for leads not contacted in 30+ days)"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of leads to return"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "send_email",
                "description": "Send personalized email to a lead",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "track_opens": {"type": "boolean", "description": "Track email opens"}
                    },
                    "required": ["lead_id", "subject", "body"]
                }
            },
            {
                "name": "send_sms",
                "description": "Send SMS to a lead",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"},
                        "message": {"type": "string", "description": "Keep under 160 characters"}
                    },
                    "required": ["lead_id", "message"]
                }
            },
            {
                "name": "create_campaign",
                "description": "Create a nurturing campaign",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "segment": {"type": "string"},
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "call"]}
                        },
                        "duration_days": {"type": "number"},
                        "touches": {"type": "number"}
                    },
                    "required": ["name", "segment", "channels"]
                }
            },
            {
                "name": "get_lead_engagement",
                "description": "Get detailed engagement metrics for a lead",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"}
                    },
                    "required": ["lead_id"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute Outreach Agent tools."""
        if tool_name == "search_leads":
            return await self._search_leads(arguments)
        elif tool_name == "send_email":
            return await self._send_email(arguments)
        elif tool_name == "send_sms":
            return await self._send_sms(arguments)
        elif tool_name == "create_campaign":
            return await self._create_campaign(arguments)
        elif tool_name == "get_lead_engagement":
            return await self._get_lead_engagement(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _search_leads(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for leads matching criteria."""
        # TODO: Implement database query
        # Mock response showing leads needing follow-up
        return {
            "leads": [
                {
                    "id": "lead_1",
                    "name": "John Smith",
                    "email": "john@example.com",
                    "phone": "+1-555-0001",
                    "status": "nurturing",
                    "temperature": "warm",
                    "last_contact": "2024-12-01",
                    "days_since_contact": 35,
                    "engagement_score": 7.5,
                    "interests": ["Riverside neighborhood", "$400-450K budget"]
                },
                {
                    "id": "lead_2",
                    "name": "Sarah Johnson",
                    "email": "sarah@example.com",
                    "phone": "+1-555-0002",
                    "status": "qualified",
                    "temperature": "hot",
                    "last_contact": "2024-12-05",
                    "days_since_contact": 38,
                    "engagement_score": 9.0,
                    "interests": ["Home seller", "CMA requested"]
                }
            ],
            "total": 2,
            "hot_count": 8,
            "warm_count": 12,
            "cold_count": 3
        }
    
    async def _send_email(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send email to a lead."""
        lead_id = args["lead_id"]
        subject = args["subject"]
        body = args["body"]
        
        logger.info(f"Sending email to lead {lead_id}", subject=subject)
        
        # TODO: Integrate with Composio for actual email sending
        return {
            "success": True,
            "lead_id": lead_id,
            "message_id": "msg_123",
            "sent_at": "2024-01-15T10:30:00Z"
        }
    
    async def _send_sms(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS to a lead."""
        lead_id = args["lead_id"]
        message = args["message"]
        
        logger.info(f"Sending SMS to lead {lead_id}")
        
        # TODO: Integrate with Composio/Twilio for actual SMS
        return {
            "success": True,
            "lead_id": lead_id,
            "message_id": "sms_456",
            "sent_at": "2024-01-15T10:30:00Z"
        }
    
    async def _create_campaign(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create nurturing campaign."""
        name = args["name"]
        segment = args["segment"]
        
        logger.info(f"Creating campaign: {name}")
        
        # TODO: Implement campaign creation
        return {
            "success": True,
            "campaign_id": "camp_789",
            "name": name,
            "segment": segment,
            "status": "draft"
        }
    
    async def _get_lead_engagement(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get lead engagement metrics."""
        lead_id = args["lead_id"]
        
        # TODO: Implement engagement tracking
        return {
            "lead_id": lead_id,
            "engagement_score": 8.5,
            "email_stats": {
                "sent": 12,
                "opened": 8,
                "clicked": 3,
                "open_rate": 66.7
            },
            "sms_stats": {
                "sent": 5,
                "replied": 2,
                "response_rate": 40.0
            },
            "last_interaction": "2024-01-10T15:30:00Z",
            "properties_viewed": 4
        }
    
    def get_temperature(self) -> float:
        """Use moderate temperature for creative yet consistent messaging."""
        return 0.7
