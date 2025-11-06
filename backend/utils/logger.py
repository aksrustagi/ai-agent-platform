"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor


def configure_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Define processors for structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def log_function_call(
    logger: structlog.stdlib.BoundLogger,
    function_name: str,
    **kwargs: Any
) -> None:
    """
    Log a function call with parameters.
    
    Args:
        logger: Structlog logger instance
        function_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger.info(
        "function_call",
        function=function_name,
        parameters=kwargs
    )


def log_llm_request(
    logger: structlog.stdlib.BoundLogger,
    provider: str,
    model: str,
    prompt_tokens: int,
    **kwargs: Any
) -> None:
    """
    Log an LLM API request.
    
    Args:
        logger: Structlog logger instance
        provider: LLM provider name (anthropic, openai, groq)
        model: Model name
        prompt_tokens: Number of prompt tokens
        **kwargs: Additional context
    """
    logger.info(
        "llm_request",
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        **kwargs
    )


def log_llm_response(
    logger: structlog.stdlib.BoundLogger,
    provider: str,
    model: str,
    completion_tokens: int,
    latency_ms: float,
    **kwargs: Any
) -> None:
    """
    Log an LLM API response.
    
    Args:
        logger: Structlog logger instance
        provider: LLM provider name
        model: Model name
        completion_tokens: Number of completion tokens
        latency_ms: Response latency in milliseconds
        **kwargs: Additional context
    """
    logger.info(
        "llm_response",
        provider=provider,
        model=model,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        **kwargs
    )


def log_agent_action(
    logger: structlog.stdlib.BoundLogger,
    agent_name: str,
    action: str,
    user_id: str,
    **kwargs: Any
) -> None:
    """
    Log an agent action.
    
    Args:
        logger: Structlog logger instance
        agent_name: Name of the agent
        action: Action being performed
        user_id: User ID
        **kwargs: Additional context
    """
    logger.info(
        "agent_action",
        agent=agent_name,
        action=action,
        user_id=user_id,
        **kwargs
    )


def log_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    context: Dict[str, Any],
) -> None:
    """
    Log an error with full context.
    
    Args:
        logger: Structlog logger instance
        error: Exception that occurred
        context: Additional context about the error
    """
    logger.error(
        "error_occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        **context,
        exc_info=True
    )
