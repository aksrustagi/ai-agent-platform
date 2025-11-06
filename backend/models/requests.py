"""Pydantic request models for API endpoints."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class AgentType(str, Enum):
    """Available agent types."""
    GROWTH = "growth"
    OUTREACH = "outreach"
    VENDOR = "vendor"
    MLS = "mls"
    TRANSACTION = "transaction"
    CONTENT = "content"
    MARKETING = "marketing"
    AUTO = "auto"  # Let coordinator decide


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Chat message."""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "How am I doing this month?",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    agent_type: AgentType = Field(default=AgentType.AUTO, description="Target agent type")
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID for context")
    include_memory: bool = Field(default=True, description="Include memory context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "message": "Find leads that need follow-up",
                "agent_type": "outreach",
                "conversation_id": "conv_abc123",
                "include_memory": True
            }
        }


class MemoryAddRequest(BaseModel):
    """Request model for adding memories."""
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    agent_id: str = Field(..., description="Agent ID")
    content: str = Field(..., min_length=1, description="Memory content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Memory metadata")
    category: Optional[str] = Field(default=None, description="Memory category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "agent_id": "growth",
                "content": "User's monthly revenue goal is $500,000",
                "metadata": {"goal_type": "revenue", "period": "monthly"},
                "category": "goals"
            }
        }


class MemorySearchRequest(BaseModel):
    """Request model for searching memories."""
    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    agent_id: Optional[str] = Field(default=None, description="Filter by agent ID")
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results")
    category: Optional[str] = Field(default=None, description="Filter by category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "agent_id": "growth",
                "query": "revenue goals",
                "limit": 10,
                "category": "goals"
            }
        }


class GoalCreateRequest(BaseModel):
    """Request model for creating goals."""
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Goal description")
    target_value: float = Field(..., gt=0, description="Target value")
    current_value: float = Field(default=0.0, ge=0, description="Current value")
    unit: str = Field(default="dollars", description="Value unit")
    deadline: Optional[datetime] = Field(default=None, description="Goal deadline")
    period: str = Field(default="monthly", description="Time period (daily, weekly, monthly, quarterly, annual)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "title": "Monthly Revenue Goal",
                "description": "Reach $500K in revenue this month",
                "target_value": 500000,
                "current_value": 320000,
                "unit": "dollars",
                "period": "monthly"
            }
        }


class CampaignCreateRequest(BaseModel):
    """Request model for creating outreach campaigns."""
    user_id: str = Field(..., description="User ID")
    name: str = Field(..., min_length=1, max_length=200, description="Campaign name")
    description: Optional[str] = Field(default=None, max_length=1000, description="Campaign description")
    segment: str = Field(..., description="Target segment")
    channels: List[str] = Field(..., min_items=1, description="Communication channels (email, sms, call)")
    duration_days: int = Field(..., gt=0, le=90, description="Campaign duration in days")
    touches: int = Field(..., ge=1, le=20, description="Number of touches")
    
    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: List[str]) -> List[str]:
        """Validate channel names."""
        valid_channels = {"email", "sms", "call", "imessage"}
        for channel in v:
            if channel.lower() not in valid_channels:
                raise ValueError(f"Invalid channel: {channel}. Must be one of {valid_channels}")
        return [c.lower() for c in v]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "name": "First-Time Buyer Nurture",
                "description": "21-day nurture campaign for first-time homebuyers",
                "segment": "first_time_buyers",
                "channels": ["email", "sms"],
                "duration_days": 21,
                "touches": 7
            }
        }


class VendorSearchRequest(BaseModel):
    """Request model for searching vendors."""
    user_id: str = Field(..., description="User ID")
    vendor_type: str = Field(..., description="Type of vendor (inspector, photographer, stager, etc.)")
    location: str = Field(..., description="Location (zip code or city)")
    min_rating: float = Field(default=4.0, ge=0, le=5, description="Minimum rating")
    max_price: Optional[float] = Field(default=None, gt=0, description="Maximum price")
    availability: Optional[str] = Field(default=None, description="Availability requirement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "vendor_type": "home_inspector",
                "location": "90210",
                "min_rating": 4.5,
                "availability": "tomorrow"
            }
        }


class PropertySearchRequest(BaseModel):
    """Request model for property search."""
    user_id: str = Field(..., description="User ID")
    location: str = Field(..., description="Location (city, zip, or address)")
    property_type: Optional[str] = Field(default=None, description="Property type")
    min_price: Optional[float] = Field(default=None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum price")
    min_beds: Optional[int] = Field(default=None, ge=0, description="Minimum bedrooms")
    max_beds: Optional[int] = Field(default=None, ge=0, description="Maximum bedrooms")
    min_baths: Optional[float] = Field(default=None, ge=0, description="Minimum bathrooms")
    max_baths: Optional[float] = Field(default=None, ge=0, description="Maximum bathrooms")
    min_sqft: Optional[int] = Field(default=None, ge=0, description="Minimum square feet")
    max_sqft: Optional[int] = Field(default=None, ge=0, description="Maximum square feet")
    keywords: Optional[List[str]] = Field(default=None, description="Search keywords")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "location": "Beverly Hills, CA",
                "property_type": "single_family",
                "min_price": 400000,
                "max_price": 600000,
                "min_beds": 3,
                "min_baths": 2,
                "limit": 20
            }
        }


class ContentGenerationRequest(BaseModel):
    """Request model for content generation."""
    user_id: str = Field(..., description="User ID")
    content_type: str = Field(..., description="Content type (social_post, blog, email, listing)")
    topic: str = Field(..., description="Content topic or subject")
    tone: str = Field(default="professional", description="Content tone")
    length: str = Field(default="medium", description="Content length (short, medium, long)")
    keywords: Optional[List[str]] = Field(default=None, description="Keywords to include")
    platform: Optional[str] = Field(default=None, description="Target platform")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "content_type": "social_post",
                "topic": "Spring home buying season tips",
                "tone": "friendly",
                "length": "short",
                "platform": "instagram"
            }
        }


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "chat_message",
                "data": {
                    "user_id": "user_123",
                    "message": "Hello",
                    "agent_type": "auto"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
