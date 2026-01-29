"""Agent module with MiniMax integration via LiteLLM."""

import os
from typing import Optional, List

from agents import Agent, Runner
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from tools import get_registered_tools


def _get_minimax_model():
    """Create a MiniMax model configuration via LiteLLM.

    Returns:
        Configured model instance for MiniMax.
    """
    # MiniMax uses OpenAI-compatible API format
    # We configure it as an OpenAI-compatible endpoint
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY environment variable is not set")

    # Create OpenAI client pointing to MiniMax endpoint
    # MiniMax uses Bearer token authentication
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.minimax.chat/v1",
        default_headers={
            "Authorization": f"Bearer {api_key}",
        },
    )

    # Use OpenAIChatCompletionsModel with MiniMax endpoint
    return OpenAIChatCompletionsModel(
        model="MiniMax-Text-01",
        openai_client=client,
    )


def create_agent(trace_id: Optional[str] = None) -> Agent:
    """Create an Agent configured to use MiniMax via LiteLLM.

    Args:
        trace_id: Optional trace ID for request tracking. If not provided,
                 a new one will be generated.

    Returns:
        Configured Agent instance.
    """
    if trace_id is None:
        from logger import create_trace_id
        trace_id = create_trace_id()

    instructions = f"""You are a helpful assistant.

Current trace_id: {trace_id}
"""

    model = _get_minimax_model()

    return Agent(
        name="MiniMax-Agent",
        instructions=instructions,
        model=model,
    )


def _load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (e.g., 'writer_v1.txt').

    Returns:
        The prompt content as a string.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", prompt_name)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def create_agent_with_tools(
    trace_id: Optional[str] = None,
    tools: Optional[List] = None,
    prompt_name: str = "writer_v1.txt"
) -> Agent:
    """Create an Agent with tools mounted.

    Args:
        trace_id: Optional trace ID for request tracking.
        tools: Optional list of tools to register. If not provided,
               will use tools from get_registered_tools().
        prompt_name: Name of the prompt file to use. Defaults to 'writer_v1.txt'.

    Returns:
        Configured Agent instance with tools.
    """
    if trace_id is None:
        from logger import create_trace_id
        trace_id = create_trace_id()

    if tools is None:
        tools = get_registered_tools()

    # Load prompt from file and append trace_id
    base_instructions = _load_prompt(prompt_name)
    instructions = f"""{base_instructions}

## 系统信息
Current trace_id: {trace_id}
"""

    model = _get_minimax_model()

    return Agent(
        name="MiniMax-Agent-With-Tools",
        instructions=instructions,
        model=model,
        tools=tools,
    )


async def run_agent(agent: Agent, prompt: str) -> Runner:
    """Run the agent with a given prompt.

    Args:
        agent: The Agent instance to run.
        prompt: The user prompt/input.

    Returns:
        RunResult from the agent execution.
    """
    result = await Runner.run(agent, prompt)
    return result
