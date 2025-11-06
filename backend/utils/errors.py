"""Custom exception classes for the AI Agent Platform."""

from typing import Any, Dict, Optional


class AgentPlatformError(Exception):
    """Base exception for all platform errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "PLATFORM_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(AgentPlatformError):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CONFIGURATION_ERROR", details)


class LLMProviderError(AgentPlatformError):
    """Raised when an LLM provider encounters an error."""

    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "LLM_PROVIDER_ERROR", details or {})
        self.provider = provider
        self.details["provider"] = provider


class AgentError(AgentPlatformError):
    """Raised when an agent encounters an error during execution."""

    def __init__(self, message: str, agent_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "AGENT_ERROR", details or {})
        self.agent_name = agent_name
        self.details["agent"] = agent_name


class MemoryError(AgentPlatformError):
    """Raised when memory operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "MEMORY_ERROR", details)


class IntegrationError(AgentPlatformError):
    """Raised when external integration fails."""

    def __init__(self, message: str, integration: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "INTEGRATION_ERROR", details or {})
        self.integration = integration
        self.details["integration"] = integration


class AuthenticationError(AgentPlatformError):
    """Raised when authentication fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(AgentPlatformError):
    """Raised when authorization fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationError(AgentPlatformError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "VALIDATION_ERROR", details or {})
        if field:
            self.details["field"] = field


class RateLimitError(AgentPlatformError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "RATE_LIMIT_ERROR", details or {})
        if retry_after:
            self.details["retry_after"] = retry_after


class CircuitBreakerError(AgentPlatformError):
    """Raised when circuit breaker is open."""

    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CIRCUIT_BREAKER_ERROR", details or {})
        self.service = service
        self.details["service"] = service


class DatabaseError(AgentPlatformError):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "DATABASE_ERROR", details)


class CacheError(AgentPlatformError):
    """Raised when cache operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CACHE_ERROR", details)


class WebSocketError(AgentPlatformError):
    """Raised when WebSocket operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "WEBSOCKET_ERROR", details)


class ToolExecutionError(AgentPlatformError):
    """Raised when tool execution fails."""

    def __init__(self, message: str, tool_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "TOOL_EXECUTION_ERROR", details or {})
        self.tool_name = tool_name
        self.details["tool"] = tool_name
