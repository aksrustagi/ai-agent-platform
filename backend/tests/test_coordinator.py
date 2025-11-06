"""Unit tests for agent coordinator."""

import pytest

from backend.coordinator.agent_coordinator import AgentCoordinator


@pytest.mark.asyncio
class TestAgentCoordinator:
    """Test Agent Coordinator."""
    
    def test_coordinator_initialization(
        self,
        mock_settings,
        mock_llm_service,
        mock_memory_manager
    ):
        """Test coordinator initializes all agents."""
        coordinator = AgentCoordinator(mock_settings, mock_llm_service, mock_memory_manager)
        
        agents = coordinator.list_agents()
        
        assert len(agents) == 7
        assert "growth" in agents
        assert "outreach" in agents
        assert "vendor" in agents
        assert "mls" in agents
        assert "transaction" in agents
        assert "content" in agents
        assert "marketing" in agents
    
    def test_get_agent(self, mock_settings, mock_llm_service, mock_memory_manager):
        """Test getting specific agent."""
        coordinator = AgentCoordinator(mock_settings, mock_llm_service, mock_memory_manager)
        
        growth_agent = coordinator.get_agent("growth")
        assert growth_agent is not None
        assert growth_agent.agent_id == "growth"
        
        invalid_agent = coordinator.get_agent("nonexistent")
        assert invalid_agent is None
    
    @pytest.mark.parametrize("message,expected_agent", [
        ("How am I doing this month?", "growth"),
        ("What's my revenue goal?", "growth"),
        ("Find leads that need follow-up", "outreach"),
        ("Send an email to John", "outreach"),
        ("I need a home inspector", "vendor"),
        ("Find 3-bedroom homes", "mls"),
        ("What's the status of my transaction?", "transaction"),
        ("Create a social media post", "content"),
        ("How are my Facebook ads doing?", "marketing"),
    ])
    async def test_message_routing(
        self,
        message,
        expected_agent,
        mock_settings,
        mock_llm_service,
        mock_memory_manager,
        sample_user_id
    ):
        """Test message routing to correct agent."""
        coordinator = AgentCoordinator(mock_settings, mock_llm_service, mock_memory_manager)
        
        response = await coordinator.route_message(
            user_id=sample_user_id,
            message=message,
            include_memory=False
        )
        
        assert response is not None
        assert response["agent_id"] == expected_agent
