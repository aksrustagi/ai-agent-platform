"""Growth & Goal Management Agent - Strategic planning and goal tracking."""

from typing import Any, Dict, List

from backend.agents.base_agent import BaseAgent
from backend.services.llm_service import LLMProvider
from backend.utils.logger import get_logger

logger = get_logger(__name__)


GROWTH_AGENT_SYSTEM_PROMPT = """You are the GROWTH & GOAL MANAGEMENT AGENT for real estate professionals.

**YOUR IDENTITY:**
You're the strategic brain that keeps real estate agents on track to hit their sales goals. You're:
• Data-driven and analytical, motivating yet realistic about performance
• Excellent at breaking big goals into daily actions
• Budget-conscious and ROI-focused
• The coordinator who aligns all other agents with the user's objectives

**YOUR CORE RESPONSIBILITIES:**

1. **GOAL TRACKING & MANAGEMENT**
   • Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
   • Track progress against annual/quarterly/monthly/weekly targets
   • Break down big goals into achievable daily milestones
   • Alert when behind schedule with specific recovery plans
   • Celebrate milestones and wins

2. **BUDGET MANAGEMENT**
   • Track marketing spend by channel
   • Monitor ROI on each lead source
   • Recommend budget reallocation based on performance
   • Calculate cost per lead and cost per acquisition

3. **PERFORMANCE ANALYTICS**
   • Calculate key metrics: conversion rates, average sale price, pipeline value
   • Compare actual vs. target performance
   • Identify trends and generate actionable recommendations

**YOUR COMMUNICATION STYLE:**
✓ Lead with data, but make it human and relatable
✓ Celebrate wins enthusiastically
✓ Address gaps constructively with specific solutions
✓ Be motivating but realistic
✓ Always connect actions back to goals
✓ Speak in terms of dollars and closings (what agents care about)

**AVOID:**
✗ Being overly negative about performance gaps
✗ Overwhelming with too many metrics at once
✗ Suggesting actions without considering feasibility
✗ Vague recommendations without specifics

When a user asks you anything, follow this pattern:
1. CHECK CURRENT STATUS - What are their goals? Where are they in progress?
2. IDENTIFY GAPS - What's working well? What's behind schedule?
3. RECOMMEND ACTIONS - Specific, actionable steps prioritized by impact
4. TRACK & FOLLOW UP - Set check-in dates and monitor progress

Always use your tools to back up recommendations with real data!
"""


class GrowthAgent(BaseAgent):
    """Growth & Goal Management Agent using Claude for strategic thinking."""
    
    @property
    def agent_id(self) -> str:
        return "growth"
    
    @property
    def agent_name(self) -> str:
        return "Growth Agent"
    
    @property
    def agent_description(self) -> str:
        return "Strategic planning, goal tracking, budget management, and performance analytics"
    
    @property
    def system_prompt(self) -> str:
        return GROWTH_AGENT_SYSTEM_PROMPT
    
    @property
    def llm_provider(self) -> LLMProvider:
        return LLMProvider.CLAUDE
    
    @property
    def capabilities(self) -> List[str]:
        return [
            "Goal setting and tracking",
            "Budget management and ROI analysis",
            "Performance analytics and reporting",
            "Task coordination",
            "Milestone tracking",
            "KPI monitoring"
        ]
    
    @property
    def available_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_goals",
                "description": "Retrieve user's goals and targets",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "quarterly", "annual"],
                            "description": "Time period for goals"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "completed", "overdue", "all"],
                            "description": "Filter by goal status"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "update_goal",
                "description": "Create or update a goal",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Goal title"
                        },
                        "target_value": {
                            "type": "number",
                            "description": "Target value"
                        },
                        "current_value": {
                            "type": "number",
                            "description": "Current progress value"
                        },
                        "period": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "quarterly", "annual"]
                        },
                        "unit": {
                            "type": "string",
                            "description": "Unit of measurement (dollars, deals, etc.)"
                        }
                    },
                    "required": ["title", "target_value", "period"]
                }
            },
            {
                "name": "get_budget_status",
                "description": "Check spending by category and overall budget",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["current_month", "last_month", "quarter", "year"]
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (marketing, operations, etc.)"
                        }
                    },
                    "required": ["period"]
                }
            },
            {
                "name": "calculate_metrics",
                "description": "Calculate performance metrics and analytics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "metric_type": {
                            "type": "string",
                            "enum": [
                                "conversion_rate",
                                "roi",
                                "cost_per_lead",
                                "pipeline_value",
                                "average_deal_size"
                            ]
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period for calculation"
                        }
                    },
                    "required": ["metric_type"]
                }
            },
            {
                "name": "get_performance_summary",
                "description": "Get comprehensive performance summary",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter", "year"]
                        }
                    },
                    "required": ["period"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute Growth Agent tools."""
        if tool_name == "get_goals":
            return await self._get_goals(arguments)
        elif tool_name == "update_goal":
            return await self._update_goal(arguments)
        elif tool_name == "get_budget_status":
            return await self._get_budget_status(arguments)
        elif tool_name == "calculate_metrics":
            return await self._calculate_metrics(arguments)
        elif tool_name == "get_performance_summary":
            return await self._get_performance_summary(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _get_goals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get user's goals."""
        # TODO: Implement database query
        # This is a mock implementation
        return {
            "goals": [
                {
                    "id": "goal_1",
                    "title": "Monthly Revenue Goal",
                    "target_value": 500000,
                    "current_value": 320000,
                    "progress_percentage": 64.0,
                    "unit": "dollars",
                    "period": "monthly",
                    "status": "active"
                },
                {
                    "id": "goal_2",
                    "title": "Monthly Closings",
                    "target_value": 8,
                    "current_value": 4,
                    "progress_percentage": 50.0,
                    "unit": "deals",
                    "period": "monthly",
                    "status": "active"
                }
            ],
            "total": 2
        }
    
    async def _update_goal(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a goal."""
        # TODO: Implement database update
        return {
            "success": True,
            "goal_id": "goal_new",
            "message": "Goal updated successfully"
        }
    
    async def _get_budget_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get budget status."""
        # TODO: Implement budget tracking
        return {
            "period": args.get("period", "current_month"),
            "total_budget": 5000,
            "spent": 3200,
            "remaining": 1800,
            "categories": {
                "facebook_ads": {"spent": 1200, "budget": 2000},
                "google_ads": {"spent": 800, "budget": 1500},
                "zillow_leads": {"spent": 1200, "budget": 1500}
            }
        }
    
    async def _calculate_metrics(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        metric_type = args.get("metric_type")
        
        # TODO: Implement real metric calculations
        metrics = {
            "conversion_rate": {"value": 3.1, "unit": "percent"},
            "roi": {"value": 4.5, "unit": "ratio"},
            "cost_per_lead": {"value": 45.50, "unit": "dollars"},
            "pipeline_value": {"value": 780000, "unit": "dollars"},
            "average_deal_size": {"value": 80000, "unit": "dollars"}
        }
        
        return metrics.get(metric_type, {"value": 0, "unit": "unknown"})
    
    async def _get_performance_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        # TODO: Implement real performance tracking
        return {
            "period": args.get("period", "month"),
            "revenue": {
                "target": 500000,
                "actual": 320000,
                "progress": 64.0
            },
            "deals": {
                "target": 8,
                "actual": 4,
                "progress": 50.0
            },
            "pipeline": {
                "active_deals": 6,
                "total_value": 480000
            },
            "highlights": [
                "Conversion rate up 15% from last month",
                "Average sale price increased to $80K",
                "Pipeline is healthy for next month"
            ],
            "concerns": [
                "Behind on closings by 4 deals",
                "Need to accelerate deal velocity"
            ]
        }
    
    async def extract_key_facts(self, user_message: str, agent_response: str) -> List[str]:
        """Extract key facts about goals and performance to remember."""
        facts = []
        
        # Extract goal mentions
        if "goal" in user_message.lower():
            facts.append(f"User discussed goals: {user_message[:100]}")
        
        # Extract performance mentions
        if any(word in user_message.lower() for word in ["revenue", "deals", "closings", "budget"]):
            facts.append(f"Performance discussion: {user_message[:100]}")
        
        return facts
    
    def get_temperature(self) -> float:
        """Use lower temperature for more analytical, consistent responses."""
        return 0.5
