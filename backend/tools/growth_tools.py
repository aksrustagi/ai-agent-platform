"""Growth Agent Tools - Goals, KPIs, Budgets, and Planning."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.integrations.tool_registry import ToolRegistry
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def track_goal(
    user_id: str,
    goal_name: str,
    target_value: float,
    current_value: float,
    deadline: str,
    unit: str = "units"
) -> Dict[str, Any]:
    """
    Track progress on a business goal.
    
    Args:
        user_id: User identifier
        goal_name: Name of the goal (e.g., "Q1 Revenue", "New Clients")
        target_value: Target value to achieve
        current_value: Current progress value
        deadline: Goal deadline (YYYY-MM-DD format)
        unit: Unit of measurement (e.g., "dollars", "clients", "listings")
    
    Returns:
        Goal tracking information with progress percentage
    """
    logger.info(f"Tracking goal: {goal_name} for user {user_id}")
    
    progress_percentage = (current_value / target_value * 100) if target_value > 0 else 0
    remaining = target_value - current_value
    is_on_track = progress_percentage >= 50  # Simple heuristic
    
    return {
        "success": True,
        "goal_id": f"goal_{user_id}_{goal_name.lower().replace(' ', '_')}",
        "goal_name": goal_name,
        "target_value": target_value,
        "current_value": current_value,
        "progress_percentage": round(progress_percentage, 2),
        "remaining": remaining,
        "unit": unit,
        "deadline": deadline,
        "status": "on_track" if is_on_track else "needs_attention",
        "days_remaining": (datetime.strptime(deadline, "%Y-%m-%d") - datetime.now()).days
    }


async def calculate_kpi(
    user_id: str,
    metric: str,
    period: str = "month"
) -> Dict[str, Any]:
    """
    Calculate KPI for a specific metric and time period.
    
    Args:
        user_id: User identifier
        metric: KPI metric name (revenue, leads, conversions, avg_deal_size, close_rate)
        period: Time period (week, month, quarter, year)
    
    Returns:
        KPI calculation with current value, trend, and comparison
    """
    logger.info(f"Calculating KPI: {metric} for {period}")
    
    # Mock KPI data - in production, would query from database
    kpi_data = {
        "revenue": {
            "current": 125000,
            "previous": 110000,
            "target": 150000
        },
        "leads": {
            "current": 45,
            "previous": 38,
            "target": 50
        },
        "conversions": {
            "current": 12,
            "previous": 10,
            "target": 15
        },
        "avg_deal_size": {
            "current": 8500,
            "previous": 8200,
            "target": 9000
        },
        "close_rate": {
            "current": 26.7,
            "previous": 26.3,
            "target": 30.0
        }
    }
    
    if metric not in kpi_data:
        return {
            "success": False,
            "error": f"Unknown metric: {metric}. Available: {list(kpi_data.keys())}"
        }
    
    data = kpi_data[metric]
    change = data["current"] - data["previous"]
    change_percentage = (change / data["previous"] * 100) if data["previous"] > 0 else 0
    target_gap = data["target"] - data["current"]
    
    return {
        "success": True,
        "metric": metric,
        "period": period,
        "current_value": data["current"],
        "previous_value": data["previous"],
        "change": round(change, 2),
        "change_percentage": round(change_percentage, 2),
        "trend": "up" if change > 0 else "down" if change < 0 else "flat",
        "target_value": data["target"],
        "target_gap": round(target_gap, 2),
        "performance": "above_target" if data["current"] >= data["target"] else "below_target"
    }


async def create_action_plan(
    user_id: str,
    goal: str,
    deadline: str,
    current_situation: str
) -> Dict[str, Any]:
    """
    Create an action plan to achieve a goal.
    
    Args:
        user_id: User identifier
        goal: The goal to achieve
        deadline: Deadline for achieving the goal (YYYY-MM-DD)
        current_situation: Description of current situation
    
    Returns:
        Structured action plan with milestones and tasks
    """
    logger.info(f"Creating action plan for goal: {goal}")
    
    # In production, would use AI to generate personalized plan
    # For now, return a structured template
    
    return {
        "success": True,
        "plan_id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "goal": goal,
        "deadline": deadline,
        "milestones": [
            {
                "milestone": "Phase 1: Assessment & Setup",
                "target_date": deadline,  # Would calculate proper dates
                "tasks": [
                    "Review current metrics and baseline",
                    "Identify key stakeholders",
                    "Set up tracking systems"
                ],
                "status": "pending"
            },
            {
                "milestone": "Phase 2: Implementation",
                "target_date": deadline,
                "tasks": [
                    "Execute primary strategies",
                    "Monitor progress weekly",
                    "Adjust tactics based on results"
                ],
                "status": "pending"
            },
            {
                "milestone": "Phase 3: Optimization",
                "target_date": deadline,
                "tasks": [
                    "Analyze what's working",
                    "Double down on successes",
                    "Course correct on failures"
                ],
                "status": "pending"
            }
        ],
        "next_action": "Review current metrics and establish baseline",
        "estimated_effort": "2-3 hours per week"
    }


async def analyze_budget(
    user_id: str,
    category: str,
    period: str = "month"
) -> Dict[str, Any]:
    """
    Analyze budget spending in a category.
    
    Args:
        user_id: User identifier
        category: Budget category (marketing, operations, technology, vendors)
        period: Time period to analyze (week, month, quarter, year)
    
    Returns:
        Budget analysis with spending, remaining budget, and recommendations
    """
    logger.info(f"Analyzing budget for category: {category}")
    
    # Mock budget data - in production, would query from database
    budget_data = {
        "marketing": {
            "allocated": 5000,
            "spent": 3200,
            "pending": 500
        },
        "operations": {
            "allocated": 8000,
            "spent": 6100,
            "pending": 800
        },
        "technology": {
            "allocated": 2000,
            "spent": 1500,
            "pending": 200
        },
        "vendors": {
            "allocated": 3000,
            "spent": 2400,
            "pending": 300
        }
    }
    
    if category not in budget_data:
        return {
            "success": False,
            "error": f"Unknown category: {category}. Available: {list(budget_data.keys())}"
        }
    
    data = budget_data[category]
    remaining = data["allocated"] - data["spent"] - data["pending"]
    utilization = ((data["spent"] + data["pending"]) / data["allocated"] * 100) if data["allocated"] > 0 else 0
    
    # Determine status
    if utilization >= 90:
        status = "critical"
        recommendation = "Budget nearly exhausted. Review spending or request increase."
    elif utilization >= 75:
        status = "warning"
        recommendation = "Monitor spending closely. Consider prioritizing essential expenses."
    else:
        status = "healthy"
        recommendation = "Budget utilization is healthy. Continue monitoring."
    
    return {
        "success": True,
        "category": category,
        "period": period,
        "allocated_budget": data["allocated"],
        "spent": data["spent"],
        "pending": data["pending"],
        "remaining": remaining,
        "utilization_percentage": round(utilization, 2),
        "status": status,
        "recommendation": recommendation,
        "top_expenses": [
            {"item": "Facebook Ads", "amount": 1200},
            {"item": "Google Ads", "amount": 1000},
            {"item": "Content Creation", "amount": 1000}
        ] if category == "marketing" else []
    }


async def forecast_revenue(
    user_id: str,
    months_ahead: int = 3,
    growth_rate: Optional[float] = None
) -> Dict[str, Any]:
    """
    Forecast revenue for upcoming months.
    
    Args:
        user_id: User identifier
        months_ahead: Number of months to forecast (1-12)
        growth_rate: Optional monthly growth rate (e.g., 0.05 for 5% growth)
    
    Returns:
        Revenue forecast with projections and confidence intervals
    """
    logger.info(f"Forecasting revenue for {months_ahead} months")
    
    if months_ahead < 1 or months_ahead > 12:
        return {
            "success": False,
            "error": "months_ahead must be between 1 and 12"
        }
    
    # Mock historical data
    current_revenue = 125000
    avg_growth_rate = growth_rate if growth_rate is not None else 0.08  # 8% default
    
    forecasts = []
    projected_revenue = current_revenue
    
    for month in range(1, months_ahead + 1):
        projected_revenue *= (1 + avg_growth_rate)
        confidence = max(50, 95 - (month * 5))  # Confidence decreases over time
        
        forecasts.append({
            "month": month,
            "projected_revenue": round(projected_revenue, 2),
            "low_estimate": round(projected_revenue * 0.85, 2),
            "high_estimate": round(projected_revenue * 1.15, 2),
            "confidence_percentage": confidence
        })
    
    return {
        "success": True,
        "current_revenue": current_revenue,
        "months_ahead": months_ahead,
        "growth_rate_used": avg_growth_rate,
        "total_projected": round(sum(f["projected_revenue"] for f in forecasts), 2),
        "forecasts": forecasts,
        "assumptions": [
            f"{avg_growth_rate * 100}% monthly growth rate",
            "Based on last 6 months of data",
            "Assumes no major market changes"
        ]
    }


def register_growth_tools(registry: ToolRegistry) -> None:
    """Register Growth Agent tools."""
    logger.info("Registering Growth Agent tools...")
    
    agents = ["growth"]
    
    # Track Goal
    registry.register_tool(
        name="track_goal",
        description="Track progress on a business goal. Use this to monitor goals like revenue targets, client acquisition, or listing goals.",
        function=track_goal,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "goal_name": {"type": "string", "description": "Name of the goal"},
                "target_value": {"type": "number", "description": "Target value to achieve"},
                "current_value": {"type": "number", "description": "Current progress value"},
                "deadline": {"type": "string", "description": "Deadline in YYYY-MM-DD format"},
                "unit": {"type": "string", "description": "Unit of measurement (dollars, clients, listings)"}
            },
            "required": ["user_id", "goal_name", "target_value", "current_value", "deadline"]
        },
        category="growth",
        agents=agents
    )
    
    # Calculate KPI
    registry.register_tool(
        name="calculate_kpi",
        description="Calculate key performance indicators like revenue, leads, conversions, close rate, or average deal size for a time period.",
        function=calculate_kpi,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "metric": {
                    "type": "string",
                    "enum": ["revenue", "leads", "conversions", "avg_deal_size", "close_rate"],
                    "description": "KPI metric to calculate"
                },
                "period": {
                    "type": "string",
                    "enum": ["week", "month", "quarter", "year"],
                    "description": "Time period for calculation"
                }
            },
            "required": ["user_id", "metric"]
        },
        category="growth",
        agents=agents
    )
    
    # Create Action Plan
    registry.register_tool(
        name="create_action_plan",
        description="Create a structured action plan to achieve a goal with milestones and tasks.",
        function=create_action_plan,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "goal": {"type": "string", "description": "The goal to achieve"},
                "deadline": {"type": "string", "description": "Deadline in YYYY-MM-DD format"},
                "current_situation": {"type": "string", "description": "Description of current situation"}
            },
            "required": ["user_id", "goal", "deadline", "current_situation"]
        },
        category="growth",
        agents=agents
    )
    
    # Analyze Budget
    registry.register_tool(
        name="analyze_budget",
        description="Analyze budget spending in a category (marketing, operations, technology, vendors) and get recommendations.",
        function=analyze_budget,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "category": {
                    "type": "string",
                    "enum": ["marketing", "operations", "technology", "vendors"],
                    "description": "Budget category to analyze"
                },
                "period": {
                    "type": "string",
                    "enum": ["week", "month", "quarter", "year"],
                    "description": "Time period to analyze"
                }
            },
            "required": ["user_id", "category"]
        },
        category="growth",
        agents=agents
    )
    
    # Forecast Revenue
    registry.register_tool(
        name="forecast_revenue",
        description="Forecast revenue for upcoming months based on historical data and growth trends.",
        function=forecast_revenue,
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User identifier"},
                "months_ahead": {"type": "integer", "description": "Number of months to forecast (1-12)"},
                "growth_rate": {"type": "number", "description": "Optional monthly growth rate (e.g., 0.05 for 5%)"}
            },
            "required": ["user_id"]
        },
        category="growth",
        agents=agents
    )
    
    logger.info("✅ Growth Agent tools registered: 5 tools")
