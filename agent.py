"""Agent module with LLM Provider integration."""

import os
from typing import Optional, List

from agents import Agent, Runner

from llm import ProviderRegistry, MiniMaxProvider
from tools import get_registered_tools


def _get_default_provider() -> MiniMaxProvider:
    """Get the default MiniMax provider from environment."""
    from llm.config import LLMConfig

    config = LLMConfig.load_provider("minimax")
    if not config:
        raise ValueError(
            "MiniMax not configured. Please set MINIMAX_API_KEY environment variable."
        )
    return MiniMaxProvider.from_config(config)


def create_agent(
    trace_id: Optional[str] = None,
    provider: Optional[MiniMaxProvider] = None,
) -> Agent:
    """Create an Agent configured to use specified provider.

    Args:
        trace_id: Optional trace ID for request tracking.
        provider: Optional provider to use. If not provided, uses MiniMax from env.

    Returns:
        Configured Agent instance.
    """
    if trace_id is None:
        from logger import create_trace_id
        trace_id = create_trace_id()

    if provider is None:
        provider = _get_default_provider()

    instructions = f"""You are a helpful assistant.

Current trace_id: {trace_id}
"""

    model = provider.create_model()

    return Agent(
        name=f"{provider.config.provider.title()}-Agent",
        instructions=instructions,
        model=model,
    )


def _load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", prompt_name)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_agent_with_tools(
    trace_id: Optional[str] = None,
    provider: Optional[MiniMaxProvider] = None,
    tools: Optional[List] = None,
    prompt_name: str = "writer_v1.txt",
) -> Agent:
    """Create an Agent with tools mounted.

    Args:
        trace_id: Optional trace ID for request tracking.
        provider: Optional provider to use. If not provided, uses MiniMax from env.
        tools: Optional list of tools to register.
        prompt_name: Name of the prompt file to use.

    Returns:
        Configured Agent instance with tools.
    """
    if trace_id is None:
        from logger import create_trace_id
        trace_id = create_trace_id()

    if provider is None:
        provider = _get_default_provider()

    if tools is None:
        tools = get_registered_tools()

    base_instructions = _load_prompt(prompt_name)
    instructions = f"""{base_instructions}

## 系统信息
Current trace_id: {trace_id}
"""

    model = provider.create_model()

    return Agent(
        name=f"{provider.config.provider.title()}-Agent-With-Tools",
        instructions=instructions,
        model=model,
        tools=tools,
    )


def create_agent_with_provider(
    provider,
    trace_id: Optional[str] = None,
    tools: Optional[List] = None,
    prompt_name: str = "writer_v1.txt",
) -> Agent:
    """Create an Agent using a specific provider.

    This is the generic version that works with any LLMProvider.

    Args:
        provider: The LLM provider to use.
        trace_id: Optional trace ID for request tracking.
        tools: Optional list of tools to register.
        prompt_name: Name of the prompt file to use.

    Returns:
        Configured Agent instance.
    """
    if trace_id is None:
        from logger import create_trace_id
        trace_id = create_trace_id()

    if tools is None:
        tools = get_registered_tools()

    base_instructions = _load_prompt(prompt_name)
    instructions = f"""{base_instructions}

## 系统信息
Current trace_id: {trace_id}
Provider: {provider.display_name}
"""

    model = provider.create_model()

    return Agent(
        name=f"{provider.config.provider.title()}-Agent",
        instructions=instructions,
        model=model,
        tools=tools,
    )


async def run_agent(agent: Agent, prompt: str) -> Runner:
    """Run the agent with a given prompt."""
    result = await Runner.run(agent, prompt)
    return result
