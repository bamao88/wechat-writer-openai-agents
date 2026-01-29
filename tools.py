"""Tools layer with latency tracking for agent tool calls."""

import time
import functools
from typing import List, Dict, Any, Callable

from agents import function_tool
from notebooklm_tool import run_search


def wrap_tool_with_latency(
    func: Callable,
    latency_records: List[Dict[str, Any]]
) -> Callable:
    """Wrap a tool function to record latency metrics.

    Args:
        func: The async function to wrap.
        latency_records: List to append latency records to.

    Returns:
        Wrapped function that records latency.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        tool_name = func.__name__

        try:
            result = await func(*args, **kwargs)
            status = "success"
            return result
        except Exception as e:
            status = f"error: {type(e).__name__}"
            raise
        finally:
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)

            latency_records.append({
                "tool_name": tool_name,
                "duration_ms": duration_ms,
                "status": status,
            })

    return wrapper


# Global latency records for tools
_tool_latency_records: List[Dict[str, Any]] = []


@function_tool
async def search_materials(query: str) -> str:
    """Search for materials on a given topic using NotebookLM.

    Args:
        query: The search query/topic to look up in the knowledge base.

    Returns:
        Search results as a string containing relevant information.
    """
    # Async tool - directly call the async run_search function
    return await run_search(query)


def get_registered_tools() -> List[Callable]:
    """Get list of all registered tools.

    Returns:
        List of callable tools decorated with function_tool.
    """
    return [search_materials]


def get_latency_records() -> List[Dict[str, Any]]:
    """Get recorded tool latencies.

    Returns:
        List of latency records.
    """
    return _tool_latency_records.copy()


def clear_latency_records():
    """Clear all latency records."""
    _tool_latency_records.clear()
