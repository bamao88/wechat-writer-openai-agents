"""Test main business flow."""

import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


def test_main_module_exists():
    """Verify main module can be imported."""
    import main
    assert hasattr(main, 'run_workflow')


@pytest.mark.asyncio
async def test_run_workflow_exists():
    """Verify run_workflow function exists and is async."""
    from main import run_workflow
    import inspect
    assert inspect.iscoroutinefunction(run_workflow)


@pytest.mark.asyncio
@patch('main.create_agent_with_tools')
async def test_workflow_returns_result(mock_create_agent, tmp_path):
    """Verify workflow returns result with all expected fields."""
    from main import run_workflow

    # Mock the agent and model
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent

    # Mock environment
    with patch.dict(os.environ, {"OUTPUT_DIR": str(tmp_path)}):
        mock_result = MagicMock()
        mock_result.final_output = "Generated article content"

        with patch('main.run_agent', return_value=mock_result):
            with patch('main.run_search', return_value="Search results"):
                result = await run_workflow("Test Topic")

    assert result is not None
    assert "topic" in result
    assert "content" in result
    assert "trace_id" in result
    assert result["topic"] == "Test Topic"
    assert result["content"] == "Generated article content"


@pytest.mark.asyncio
@patch('main.create_agent_with_tools')
async def test_workflow_saves_file(mock_create_agent, tmp_path):
    """Verify workflow saves output to file."""
    from main import run_workflow

    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent

    with patch.dict(os.environ, {"OUTPUT_DIR": str(tmp_path)}):
        mock_result = MagicMock()
        mock_result.final_output = "Article content"

        with patch('main.run_agent', return_value=mock_result):
            with patch('main.run_search', return_value="Search results"):
                result = await run_workflow("Test Topic")

    # Check file was created
    output_files = list(tmp_path.glob("*.md"))
    assert len(output_files) >= 1


@pytest.mark.asyncio
@patch('main.create_agent_with_tools')
async def test_workflow_calls_search(mock_create_agent):
    """Verify workflow calls search before generating."""
    from main import run_workflow

    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent

    mock_search = AsyncMock(return_value="Search results for topic")
    mock_result = MagicMock()
    mock_result.final_output = "Generated content"

    with patch('main.run_search', mock_search):
        with patch('main.run_agent', return_value=mock_result):
            await run_workflow("AI Technology")

    # Search should be called
    mock_search.assert_called_once()


@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Verify workflow handles errors gracefully."""
    from main import run_workflow

    with pytest.raises(Exception):
        with patch('main.run_search', side_effect=Exception("Search failed")):
            await run_workflow("Test Topic")


def test_save_report_exists():
    """Verify save_report function exists."""
    from main import save_report
    assert callable(save_report)
