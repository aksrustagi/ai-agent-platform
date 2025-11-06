"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.config import Settings
from backend.memory.memory_manager import MemoryManager
from backend.services.llm_service import LLMService


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        secret_key="test-secret-key",
        anthropic_api_key="test-anthropic-key",
        openai_api_key="test-openai-key",
        groq_api_key="test-groq-key",
        mem0_api_key="test-mem0-key",
        composio_api_key="test-composio-key",
        realestate_api_key="test-realestate-key",
        postgres_password="test-password",
        debug=True,
        app_env="testing"
    )


@pytest.fixture
def mock_llm_service(mock_settings):
    """Mock LLM service for testing."""
    service = MagicMock(spec=LLMService)
    service.generate = AsyncMock(return_value={
        "content": "Test response",
        "tool_calls": None,
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "provider": "claude",
        "model": "claude-3-5-sonnet"
    })
    return service


@pytest.fixture
def mock_memory_manager(mock_settings):
    """Mock memory manager for testing."""
    manager = MagicMock(spec=MemoryManager)
    manager.get_context_for_agent = AsyncMock(return_value="Test context")
    manager.store_conversation_context = AsyncMock(return_value=[])
    return manager


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return "test_user_123"


@pytest.fixture
def sample_message():
    """Sample user message for testing."""
    return "How am I doing this month?"
