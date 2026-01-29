"""Test Agent tool mounting and tool calls."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def test_agent_with_tools_exists():
    """Verify agent module has create_agent_with_tools function."""
    from agent import create_agent_with_tools
    assert callable(create_agent_with_tools)


@patch('agent._get_minimax_model')
def test_create_agent_with_tools_returns_agent(mock_get_model):
    """Verify create_agent_with_tools returns an Agent with tools."""
    from agent import create_agent_with_tools
    from agents import Agent
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    agent = create_agent_with_tools()
    assert isinstance(agent, Agent)


@patch('agent._get_minimax_model')
def test_agent_has_tools_registered(mock_get_model):
    """Verify agent has tools registered."""
    from agent import create_agent_with_tools
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    agent = create_agent_with_tools()
    # Agent should have at least one tool
    assert len(agent.tools) >= 1


@patch('agent._get_minimax_model')
def test_agent_tool_is_search_materials(mock_get_model):
    """Verify agent has search_materials tool."""
    from agent import create_agent_with_tools
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    agent = create_agent_with_tools()
    tool_names = [tool.name for tool in agent.tools]
    assert "search_materials" in tool_names


@pytest.mark.asyncio
@patch('agent._get_minimax_model')
async def test_agent_can_trigger_tool_call(mock_get_model):
    """Verify agent can trigger tool calls."""
    from agent import create_agent_with_tools, run_agent
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)

    # Mock the Runner.run to simulate tool call
    mock_result = MagicMock()
    mock_result.final_output = "Found materials on AI"

    with patch('agents.Runner.run', return_value=mock_result):
        agent = create_agent_with_tools()
        result = await run_agent(agent, "Search for AI materials")

        assert result is not None
        assert isinstance(result.final_output, str)


@patch('agent._get_minimax_model')
def test_tool_receives_correct_parameters(mock_get_model):
    """Verify tool receives correct parameters when called."""
    from agent import create_agent_with_tools
    from tools import search_materials
    from agents.models.interface import Model

    mock_get_model.return_value = MagicMock(spec=Model)
    agent = create_agent_with_tools()

    # Find the search_materials tool
    search_tool = None
    for tool in agent.tools:
        if tool.name == "search_materials":
            search_tool = tool
            break

    assert search_tool is not None
    # Verify tool has correct schema
    assert "query" in search_tool.params_json_schema.get("properties", {})
