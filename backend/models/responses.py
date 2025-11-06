"""Pydantic response models for API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.models.requests import AgentType, MessageRole


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
    services: Dict[str, bool] = Field(..., description="Service availability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "database": True,
                    "redis": True,
                    "llm": True
                }
            }
        }


class MessageResponse(BaseModel):
    """Single message response."""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str = Field(..., description="Conversation ID")
    agent_type: AgentType = Field(..., description="Agent that handled the request")
    agent_name: str = Field(..., description="Friendly agent name")
    message: MessageResponse = Field(..., description="Assistant's response")
    suggested_actions: Optional[List[str]] = Field(default=None, description="Suggested follow-up actions")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="Tools used by the agent")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    tokens_used: Optional[Dict[str, int]] = Field(default=None, description="Token usage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_abc123",
                "agent_type": "growth",
                "agent_name": "Growth Agent",
                "message": {
                    "role": "assistant",
                    "content": "Let's look at your progress! You're at 64% to goal...",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "suggested_actions": [
                    "Review pipeline details",
                    "Contact hot leads",
                    "Schedule follow-ups"
                ],
                "processing_time_ms": 1250.5,
                "tokens_used": {
                    "prompt": 150,
                    "completion": 450,
                    "total": 600
                }
            }
        }


class AgentInfo(BaseModel):
    """Information about an agent."""
    agent_type: AgentType = Field(..., description="Agent type")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    llm_provider: str = Field(..., description="LLM provider used")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    available_tools: List[str] = Field(..., description="Available tools")


class AgentListResponse(BaseModel):
    """List of available agents."""
    agents: List[AgentInfo] = Field(..., description="Available agents")
    total: int = Field(..., description="Total number of agents")


class MemoryItem(BaseModel):
    """Single memory item."""
    id: str = Field(..., description="Memory ID")
    user_id: str = Field(..., description="User ID")
    agent_id: str = Field(..., description="Agent ID")
    content: str = Field(..., description="Memory content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Memory metadata")
    category: Optional[str] = Field(default=None, description="Memory category")
    created_at: datetime = Field(..., description="Creation timestamp")
    relevance_score: Optional[float] = Field(default=None, description="Relevance score for search results")


class MemoryResponse(BaseModel):
    """Response for memory operations."""
    memories: List[MemoryItem] = Field(..., description="Memory items")
    total: int = Field(..., description="Total number of memories")


class GoalResponse(BaseModel):
    """Response model for goal."""
    id: str = Field(..., description="Goal ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Goal title")
    description: Optional[str] = Field(default=None, description="Goal description")
    target_value: float = Field(..., description="Target value")
    current_value: float = Field(..., description="Current value")
    progress_percentage: float = Field(..., description="Progress percentage")
    unit: str = Field(..., description="Value unit")
    period: str = Field(..., description="Time period")
    status: str = Field(..., description="Goal status (active, completed, overdue)")
    deadline: Optional[datetime] = Field(default=None, description="Goal deadline")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CampaignResponse(BaseModel):
    """Response model for campaign."""
    id: str = Field(..., description="Campaign ID")
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., description="Campaign name")
    description: Optional[str] = Field(default=None, description="Campaign description")
    segment: str = Field(..., description="Target segment")
    channels: List[str] = Field(..., description="Communication channels")
    status: str = Field(..., description="Campaign status (draft, active, paused, completed)")
    stats: Dict[str, Any] = Field(..., description="Campaign statistics")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")


class VendorInfo(BaseModel):
    """Vendor information."""
    id: str = Field(..., description="Vendor ID")
    name: str = Field(..., description="Vendor name")
    vendor_type: str = Field(..., description="Vendor type")
    rating: float = Field(..., description="Average rating")
    review_count: int = Field(..., description="Number of reviews")
    price_range: str = Field(..., description="Price range indicator")
    contact: Dict[str, str] = Field(..., description="Contact information")
    availability: Optional[str] = Field(default=None, description="Availability information")
    specialties: List[str] = Field(..., description="Vendor specialties")
    insurance_verified: bool = Field(..., description="Insurance verification status")
    license_number: Optional[str] = Field(default=None, description="License number")


class VendorSearchResponse(BaseModel):
    """Response for vendor search."""
    vendors: List[VendorInfo] = Field(..., description="Matching vendors")
    total: int = Field(..., description="Total number of results")
    recommendation: Optional[str] = Field(default=None, description="Vendor ID of recommended option")


class PropertyInfo(BaseModel):
    """Property information."""
    id: str = Field(..., description="Property ID")
    address: str = Field(..., description="Property address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., description="ZIP code")
    price: float = Field(..., description="List price")
    beds: int = Field(..., description="Number of bedrooms")
    baths: float = Field(..., description="Number of bathrooms")
    sqft: int = Field(..., description="Square footage")
    property_type: str = Field(..., description="Property type")
    status: str = Field(..., description="Listing status")
    days_on_market: Optional[int] = Field(default=None, description="Days on market")
    photos: List[str] = Field(default_factory=list, description="Photo URLs")
    description: Optional[str] = Field(default=None, description="Property description")
    features: List[str] = Field(default_factory=list, description="Property features")


class PropertySearchResponse(BaseModel):
    """Response for property search."""
    properties: List[PropertyInfo] = Field(..., description="Matching properties")
    total: int = Field(..., description="Total number of results")
    market_summary: Optional[Dict[str, Any]] = Field(default=None, description="Market statistics")


class ContentResponse(BaseModel):
    """Response for content generation."""
    content: str = Field(..., description="Generated content")
    content_type: str = Field(..., description="Content type")
    metadata: Dict[str, Any] = Field(..., description="Content metadata")
    variations: Optional[List[str]] = Field(default=None, description="Content variations")
    suggested_hashtags: Optional[List[str]] = Field(default=None, description="Suggested hashtags")
    suggested_times: Optional[List[str]] = Field(default=None, description="Best posting times")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Invalid input parameters",
                "details": {
                    "field": "email",
                    "issue": "Invalid email format"
                },
                "request_id": "req_abc123",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {
                    "id": "abc123",
                    "status": "created"
                }
            }
        }
