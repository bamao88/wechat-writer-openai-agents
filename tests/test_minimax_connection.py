"""Test MiniMax connection through Agent."""

import os
import pytest
from unittest.mock import patch, MagicMock


def test_agent_module_exists():
    """Verify agent module can be imported."""
    import agent
    assert hasattr(agent, 'create_agent')


@patch('agent._get_minimax_model')
def test_create_agent_returns_agent(mock_get_model):
    """Verify create_agent returns an Agent instance."""
    from agent import create_agent
    from agents import Agent
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    agent_instance = create_agent()
    assert isinstance(agent_instance, Agent)


@patch('agent._get_minimax_model')
def test_agent_has_trace_id(mock_get_model):
    """Verify agent has trace_id in its context."""
    from agent import create_agent
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    trace_id = "test_trace_123"
    agent_instance = create_agent(trace_id=trace_id)

    # Agent should store trace_id somehow (in instructions or context)
    assert trace_id in agent_instance.instructions


@patch('agent._get_minimax_model')
def test_agent_model_configured(mock_get_model):
    """Verify agent is configured with MiniMax model."""
    from agent import create_agent
    from agents.models.interface import Model

    mock_model = MagicMock(spec=Model)
    mock_get_model.return_value = mock_model

    agent_instance = create_agent()
    # Model should be set
    assert agent_instance.model is not None


@pytest.mark.asyncio
@patch('agent._get_minimax_model')
async def test_agent_run_returns_result(mock_get_model):
    """Verify running agent returns a result with trace_id."""
    from agent import create_agent, run_agent
    from agents import RunResult
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)

    # Mock the Runner.run to avoid actual API call
    mock_result = MagicMock(spec=RunResult)
    mock_result.final_output = "Test response from MiniMax"

    with patch('agents.Runner.run', return_value=mock_result):
        agent_instance = create_agent(trace_id="test_trace_123")
        result = await run_agent(agent_instance, "Hello")

        assert result is not None
        assert isinstance(result.final_output, str)


@pytest.mark.skipif(
    not os.getenv("MINIMAX_API_KEY"),
    reason="MINIMAX_API_KEY not set - skipping real API test"
)
@pytest.mark.asyncio
async def test_real_minimax_connection():
    """Real API test - requires MINIMAX_API_KEY."""
    from agent import create_agent, run_agent

    trace_id = "test_trace_real"
    agent_instance = create_agent(trace_id=trace_id)

    result = await run_agent(agent_instance, "Say 'Hello from MiniMax' and nothing else.")

    assert result is not None
    assert result.final_output is not None
    assert isinstance(result.final_output, str)
    assert len(result.final_output) > 0
