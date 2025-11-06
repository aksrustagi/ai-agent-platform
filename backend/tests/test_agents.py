"""Unit tests for agents."""

import pytest

from backend.agents.growth_agent import GrowthAgent
from backend.agents.outreach_agent import OutreachAgent
from backend.services.llm_service import LLMProvider


@pytest.mark.asyncio
class TestGrowthAgent:
    """Test Growth Agent."""
    
    def test_agent_properties(self, mock_settings, mock_llm_service, mock_memory_manager):
        """Test agent properties are correctly set."""
        agent = GrowthAgent(mock_settings, mock_llm_service, mock_memory_manager)
        
        assert agent.agent_id == "growth"
        assert agent.agent_name == "Growth Agent"
        assert agent.llm_provider == LLMProvider.CLAUDE
        assert len(agent.capabilities) > 0
        assert len(agent.available_tools) > 0
    
    async def test_process_message(
        self,
        mock_settings,
        mock_llm_service,
        mock_memory_manager,
        sample_user_id,
        sample_message
    ):
        """Test processing a message."""
        agent = GrowthAgent(mock_settings, mock_llm_service, mock_memory_manager)
        
        response = await agent.process_message(
            user_id=sample_user_id,
            message=sample_message,
            include_memory=True
        )
        
        assert response is not None
        assert "agent_id" in response
        assert response["agent_id"] == "growth"
        assert "content" in response
        assert mock_llm_service.generate.called


@pytest.mark.asyncio
class TestOutreachAgent:
    """Test Outreach Agent."""
    
    def test_agent_properties(self, mock_settings, mock_llm_service, mock_memory_manager):
        """Test agent properties are correctly set."""
        agent = OutreachAgent(mock_settings, mock_llm_service, mock_memory_manager)
        
        assert agent.agent_id == "outreach"
        assert agent.agent_name == "Outreach Agent"
        assert agent.llm_provider == LLMProvider.GPT4
        assert len(agent.capabilities) > 0
        assert len(agent.available_tools) > 0
    
    async def test_process_message(
        self,
        mock_settings,
        mock_llm_service,
        mock_memory_manager,
        sample_user_id
    ):
        """Test processing a message."""
        agent = OutreachAgent(mock_settings, mock_llm_service, mock_memory_manager)
        
        response = await agent.process_message(
            user_id=sample_user_id,
            message="Find leads that need follow-up",
            include_memory=True
        )
        
        assert response is not None
        assert response["agent_id"] == "outreach"
        assert "content" in response
