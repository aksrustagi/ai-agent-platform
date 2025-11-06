"""SQLAlchemy database models."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(String(100), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    api_key_hash = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Conversation(Base):
    """Conversation model for tracking chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)
    title = Column(String(255))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_updated', 'user_id', 'updated_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, agent_type={self.agent_type})>"


class Message(Base):
    """Message model for storing chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    tokens_used = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"


class Goal(Base):
    """Goal model for tracking user goals."""
    
    __tablename__ = "goals"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50), default="dollars")
    period = Column(String(50), default="monthly")  # daily, weekly, monthly, quarterly, annual
    status = Column(String(50), default="active")  # active, completed, overdue, cancelled
    deadline = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_period', 'user_id', 'period'),
    )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.target_value == 0:
            return 0.0
        return min((self.current_value / self.target_value) * 100, 100.0)
    
    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, title={self.title}, progress={self.progress_percentage:.1f}%)>"


class Campaign(Base):
    """Campaign model for outreach campaigns."""
    
    __tablename__ = "campaigns"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    segment = Column(String(100), nullable=False)
    channels = Column(JSON, nullable=False)  # List of channels: email, sms, call
    duration_days = Column(Integer, nullable=False)
    touches = Column(Integer, nullable=False)
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    stats = Column(JSON, default=dict)  # Campaign statistics
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name={self.name}, status={self.status})>"


class Lead(Base):
    """Lead model for tracking leads."""
    
    __tablename__ = "leads"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)  # Agent user ID
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    status = Column(String(50), default="new")  # new, contacted, qualified, nurturing, converted, lost
    temperature = Column(String(20), default="cold")  # hot, warm, cold
    source = Column(String(100))  # Where the lead came from
    budget_min = Column(Float)
    budget_max = Column(Float)
    timeline = Column(String(100))
    preferences = Column(JSON)  # Property preferences, communication preferences, etc.
    engagement_score = Column(Float, default=0.0)
    last_contact_at = Column(DateTime(timezone=True))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_temperature', 'user_id', 'temperature'),
        Index('idx_user_last_contact', 'user_id', 'last_contact_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, name={self.first_name} {self.last_name}, status={self.status})>"


class Vendor(Base):
    """Vendor model for storing vendor information."""
    
    __tablename__ = "vendors"
    
    id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    vendor_type = Column(String(100), nullable=False, index=True)  # inspector, photographer, stager, etc.
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(500))
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    price_range = Column(String(20))  # $, $$, $$$
    service_area = Column(JSON)  # List of zip codes or cities served
    specialties = Column(JSON)  # List of specialties
    license_number = Column(String(100))
    insurance_verified = Column(Boolean, default=False)
    availability = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_type_rating', 'vendor_type', 'rating'),
    )
    
    def __repr__(self) -> str:
        return f"<Vendor(id={self.id}, name={self.name}, type={self.vendor_type})>"


class Property(Base):
    """Property model for storing property information."""
    
    __tablename__ = "properties"
    
    id = Column(String(100), primary_key=True)
    mls_id = Column(String(100), unique=True, index=True)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    beds = Column(Integer)
    baths = Column(Float)
    sqft = Column(Integer)
    property_type = Column(String(50), nullable=False)  # single_family, condo, townhouse, etc.
    status = Column(String(50), default="active")  # active, pending, sold, withdrawn
    days_on_market = Column(Integer)
    description = Column(Text)
    features = Column(JSON)
    photos = Column(JSON)
    coordinates = Column(JSON)  # lat, lng
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_location_price', 'city', 'state', 'price'),
        Index('idx_zip_status', 'zip_code', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<Property(id={self.id}, address={self.address}, price=${self.price})>"


class Transaction(Base):
    """Transaction model for tracking real estate transactions."""
    
    __tablename__ = "transactions"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)  # Agent user ID
    property_id = Column(String(100))
    transaction_type = Column(String(50), nullable=False)  # listing, purchase
    status = Column(String(50), default="draft")  # draft, pending, in_progress, completed, cancelled
    price = Column(Float)
    commission = Column(Float)
    client_name = Column(String(255))
    client_email = Column(String(255))
    client_phone = Column(String(50))
    expected_close_date = Column(DateTime(timezone=True))
    actual_close_date = Column(DateTime(timezone=True))
    documents = Column(JSON)  # List of document references
    notes = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_close_date', 'user_id', 'expected_close_date'),
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type={self.transaction_type}, status={self.status})>"
