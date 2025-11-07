"""Application configuration using Pydantic settings."""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Settings
    app_name: str = Field(default="AI Agent Platform", description="Application name")
    app_env: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Server Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    workers: int = Field(default=4, description="Number of workers")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT signing")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    
    # LLM API Keys
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    openai_api_key: str = Field(..., description="OpenAI API key")
    groq_api_key: str = Field(..., description="Groq API key")
    
    # LLM Model Configuration
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model name")
    gpt4_model: str = Field(default="gpt-4-turbo-preview", description="GPT-4 model name")
    groq_model: str = Field(default="llama-3.1-70b-versatile", description="Groq model name")
    
    # Mem0 Configuration
    mem0_api_key: str = Field(..., description="Mem0 API key")
    mem0_base_url: str = Field(default="https://api.mem0.ai", description="Mem0 base URL")
    
    # Composio Configuration
    composio_api_key: str = Field(..., description="Composio API key")
    
    # RealEstateAPI Configuration
    realestate_api_key: str = Field(..., description="RealEstateAPI key")
    realestate_base_url: str = Field(
        default="https://api.realestateapi.com",
        description="RealEstateAPI base URL"
    )
    
    # MediaMagic API Configuration
    mediamagic_api_url: Optional[str] = Field(
        default=None,
        description="MediaMagic API URL for media processing"
    )
    mediamagic_api_key: Optional[str] = Field(
        default=None,
        description="MediaMagic API key"
    )
    
    # Go Services Configuration
    go_services_url: Optional[str] = Field(
        default=None,
        description="Go Services base URL"
    )
    go_services_api_key: Optional[str] = Field(
        default=None,
        description="Go Services API key"
    )
    
    # MCP Server Configuration
    mcp_server_url: Optional[str] = Field(
        default=None,
        description="MCP server base URL"
    )
    mcp_enable_remote: bool = Field(
        default=True,
        description="Enable remote MCP server communication"
    )
    
    # PostgreSQL Database
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="ai_agent_platform", description="PostgreSQL database name")
    postgres_user: str = Field(default="postgres", description="PostgreSQL user")
    postgres_password: str = Field(..., description="PostgreSQL password")
    database_url: Optional[str] = Field(default=None, description="Full database URL")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_url: Optional[str] = Field(default=None, description="Full Redis URL")
    
    # WebSocket Configuration
    websocket_ping_interval: int = Field(default=30, description="WebSocket ping interval in seconds")
    websocket_ping_timeout: int = Field(default=10, description="WebSocket ping timeout in seconds")
    websocket_max_connections: int = Field(default=100, description="Maximum WebSocket connections")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Max requests per period")
    rate_limit_period: int = Field(default=60, description="Rate limit period in seconds")
    
    # Retry Configuration
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, description="Retry backoff multiplier")
    retry_timeout: int = Field(default=30, description="Retry timeout in seconds")
    
    # Circuit Breaker Configuration
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        description="Failures before opening circuit"
    )
    circuit_breaker_recovery_timeout: int = Field(
        default=60,
        description="Circuit recovery timeout in seconds"
    )
    
    # Caching
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: any) -> List[str]:
        """Parse allowed origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def database_url_composed(self) -> str:
        """Compose database URL from components."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url_composed(self) -> str:
        """Compose Redis URL from components."""
        if self.redis_url:
            return self.redis_url
        
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton.
    
    Returns:
        Settings instance
    """
    global settings
    if settings is None:
        settings = Settings()
    return settings
