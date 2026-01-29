"""Test tools layer with latency tracking."""

import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock


def test_tools_module_exists():
    """Verify tools module can be imported."""
    import tools
    assert hasattr(tools, 'wrap_tool_with_latency')


def test_wrap_tool_with_latency_exists():
    """Verify wrap_tool_with_latency function exists."""
    from tools import wrap_tool_with_latency
    assert callable(wrap_tool_with_latency)


@pytest.mark.asyncio
async def test_tool_latency_recorded():
    """Verify tool latency is recorded when wrapped tool is called."""
    from tools import wrap_tool_with_latency

    # Create a mock async function
    async def mock_tool(query: str) -> str:
        return f"Result for {query}"

    latency_records = []
    wrapped = wrap_tool_with_latency(mock_tool, latency_records)

    result = await wrapped("test query")

    assert result == "Result for test query"
    assert len(latency_records) == 1
    assert "duration_ms" in latency_records[0]
    assert "tool_name" in latency_records[0]
    assert latency_records[0]["tool_name"] == "mock_tool"


@pytest.mark.asyncio
async def test_tool_latency_timing():
    """Verify tool latency timing is reasonable."""
    from tools import wrap_tool_with_latency

    async def slow_tool(query: str) -> str:
        # Simulate some work
        time.sleep(0.01)  # 10ms
        return "done"

    latency_records = []
    wrapped = wrap_tool_with_latency(slow_tool, latency_records)

    await wrapped("test")

    assert len(latency_records) == 1
    duration = latency_records[0]["duration_ms"]
    # Should be at least 10ms (our sleep) but not too large
    assert duration >= 10
    assert duration < 1000  # Less than 1 second


@pytest.mark.asyncio
async def test_tool_error_handled():
    """Verify tool errors are handled gracefully."""
    from tools import wrap_tool_with_latency

    async def failing_tool(query: str) -> str:
        raise ValueError("Tool failed")

    latency_records = []
    wrapped = wrap_tool_with_latency(failing_tool, latency_records)

    with pytest.raises(ValueError):
        await wrapped("test")

    # Should still record latency even on failure
    assert len(latency_records) == 1
    assert latency_records[0]["tool_name"] == "failing_tool"


def test_get_registered_tools():
    """Verify get_registered_tools returns list of tools."""
    from tools import get_registered_tools

    tools_list = get_registered_tools()
    assert isinstance(tools_list, list)
    # Should have at least the notebooklm search tool
    assert len(tools_list) >= 1


def test_tool_has_function_tool_decorator():
    """Verify tools have the function_tool decorator applied."""
    from tools import get_registered_tools
    from agents import FunctionTool

    tools_list = get_registered_tools()

    for tool in tools_list:
        # Each tool should be a FunctionTool instance (returned by @function_tool)
        assert isinstance(tool, FunctionTool)
