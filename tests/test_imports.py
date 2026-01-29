"""Test that all required dependencies can be imported."""

import pytest


def test_openai_agents_import():
    """Verify openai-agents package can be imported."""
    import agents
    assert agents is not None


def test_litellm_import():
    """Verify litellm package can be imported."""
    import litellm
    assert litellm is not None


def test_pydantic_import():
    """Verify pydantic package can be imported."""
    import pydantic
    assert pydantic is not None


def test_agents_module_has_required_classes():
    """Verify agents module has required classes for Agent and Runner."""
    import agents
    assert hasattr(agents, 'Agent')
    assert hasattr(agents, 'Runner')


def test_agents_module_has_function_tool():
    """Verify agents module has function_tool decorator."""
    import agents
    assert hasattr(agents, 'function_tool')
