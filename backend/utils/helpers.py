"""General utility helper functions."""

import asyncio
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from backend.utils.errors import AgentPlatformError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


def async_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Multiplier for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {wait_time}s",
                            function=func.__name__,
                            error=str(e)
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed",
                            function=func.__name__,
                            error=str(e)
                        )
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Args:
        func: Function to measure
    
    Returns:
        Decorated function
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        elapsed_ms = (time.time() - start_time) * 1000
        logger.debug(
            f"Function {func.__name__} took {elapsed_ms:.2f}ms",
            function=func.__name__,
            duration_ms=elapsed_ms
        )
        return result
    
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start_time) * 1000
        logger.debug(
            f"Function {func.__name__} took {elapsed_ms:.2f}ms",
            function=func.__name__,
            duration_ms=elapsed_ms
        )
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunked lists
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = '',
    sep: str = '.'
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator between keys
    
    Returns:
        Flattened dictionary
    """
    items: List[tuple] = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime object (defaults to now)
        format_str: Format string
    
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.strftime(format_str)


def parse_bool(value: Any) -> bool:
    """
    Parse a value as a boolean.
    
    Args:
        value: Value to parse
    
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    
    return bool(value)


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with nested keys.
    
    Args:
        dictionary: Dictionary to search
        key: Key path (e.g., 'user.profile.name')
        default: Default value if key not found
    
    Returns:
        Value or default
    """
    keys = key.split('.')
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    """
    result: Dict[str, Any] = {}
    
    for d in dicts:
        result.update(d)
    
    return result


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for fault tolerance.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "default"
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Call a function through the circuit breaker.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Function result
        
        Raises:
            AgentPlatformError: If circuit is open
        """
        if self.state == "open":
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                logger.info(f"Circuit breaker {self.name} entering half-open state")
            else:
                from backend.utils.errors import CircuitBreakerError
                raise CircuitBreakerError(
                    f"Circuit breaker {self.name} is open",
                    service=self.name
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        if self.state == "half-open":
            self.state = "closed"
            logger.info(f"Circuit breaker {self.name} closed")
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker {self.name} opened",
                failure_count=self.failure_count
            )
