---
wave: 2
depends_on:
  - "01-PLAN.md"
files_modified:
  - llm/providers.py
  - llm/__init__.py
  - agent.py
  - tests/test_providers.py
autonomous: true
must_haves:
  - MiniMaxProvider implements LLMProvider interface
  - MiniMaxProvider.from_config() creates instance from ProviderConfig
  - create_model() returns OpenAIChatCompletionsModel
  - agent.py refactored to use provider abstraction
  - Existing functionality preserved (backward compatible)
  - Unit tests pass for MiniMaxProvider
---

# Plan 02: MiniMax Provider Implementation

## Objective

Implement MiniMaxProvider by extracting and refactoring existing MiniMax integration code.

## Context

Current implementation in `agent.py`:

```python
def _get_minimax_model():
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY environment variable is not set")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.minimax.chat/v1",
        default_headers={
            "Authorization": f"Bearer {api_key}",
        },
    )

    return OpenAIChatCompletionsModel(
        model="MiniMax-Text-01",
        openai_client=client,
    )
```

This needs to be moved into a proper MiniMaxProvider class.

## Tasks

### Task 1: Implement MiniMaxProvider

Create `llm/providers.py`:

```python
from openai import AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from llm.base import LLMProvider, ModelConfig
from llm.config import ProviderConfig


class MiniMaxProvider(LLMProvider):
    """MiniMax API provider implementation."""

    def __init__(self, config: ModelConfig):
        self._config = config
        self._client = None
        self._model = None

    @classmethod
    def from_config(cls, config: ProviderConfig) -> "MiniMaxProvider":
        """Create provider from configuration."""
        model_config = ModelConfig(
            name=f"MiniMax-{config.model}",
            provider="minimax",
            model_id=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        return cls(model_config)

    def create_model(self) -> OpenAIChatCompletionsModel:
        """Create MiniMax model instance."""
        if self._model is None:
            self._client = AsyncOpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
                default_headers={
                    "Authorization": f"Bearer {self._config.api_key}",
                },
            )
            self._model = OpenAIChatCompletionsModel(
                model=self._config.model_id,
                openai_client=self._client,
            )
        return self._model

    @property
    def config(self) -> ModelConfig:
        return self._config

    @property
    def display_name(self) -> str:
        return f"MiniMax-{self._config.model_id}"
```

### Task 2: Register Provider Class

Update `llm/__init__.py`:

```python
from llm.base import LLMProvider, ModelConfig
from llm.config import LLMConfig, ProviderConfig
from llm.registry import ProviderRegistry
from llm.providers import MiniMaxProvider

# Register provider classes
ProviderRegistry.register_class("minimax", MiniMaxProvider)

__all__ = [
    "LLMProvider",
    "ModelConfig",
    "LLMConfig",
    "ProviderConfig",
    "ProviderRegistry",
    "MiniMaxProvider",
]
```

### Task 3: Refactor agent.py to Use Provider

Update `agent.py` to use the new provider system:

```python
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


async def run_agent(agent: Agent, prompt: str) -> Runner:
    """Run the agent with a given prompt."""
    result = await Runner.run(agent, prompt)
    return result
```

### Task 4: Add create_agent_with_provider Function

Add to `agent.py`:

```python
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
```

### Task 5: Create Unit Tests

Create `tests/test_providers.py`:

```python
"""Tests for LLM providers."""

import pytest
from unittest.mock import MagicMock, patch

from llm.providers import MiniMaxProvider
from llm.config import ProviderConfig
from llm.base import ModelConfig


class TestMiniMaxProvider:
    """Test MiniMaxProvider implementation."""

    def test_from_config(self):
        """Test creating provider from config."""
        config = ProviderConfig(
            provider_id='minimax',
            api_key='test-key',
            base_url='https://test.minimax.chat/v1',
            model='Test-Model',
        )
        provider = MiniMaxProvider.from_config(config)

        assert provider.config.provider == 'minimax'
        assert provider.config.model_id == 'Test-Model'
        assert provider.display_name == 'MiniMax-Test-Model'

    def test_config_property(self):
        """Test config property returns ModelConfig."""
        model_config = ModelConfig(
            name="MiniMax-Test",
            provider="minimax",
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com",
        )
        provider = MiniMaxProvider(model_config)

        assert provider.config == model_config

    def test_display_name(self):
        """Test display_name property."""
        model_config = ModelConfig(
            name="MiniMax-Test",
            provider="minimax",
            model_id="test-model",
            api_key="test-key",
            base_url="https://test.com",
        )
        provider = MiniMaxProvider(model_config)

        assert provider.display_name == "MiniMax-test-model"

    def test_implements_interface(self):
        """Test MiniMaxProvider implements LLMProvider interface."""
        from llm.base import LLMProvider

        config = ProviderConfig(
            provider_id='minimax',
            api_key='test-key',
            base_url='https://test.com',
            model='test',
        )
        provider = MiniMaxProvider.from_config(config)

        assert isinstance(provider, LLMProvider)
        assert hasattr(provider, 'create_model')
        assert hasattr(provider, 'config')
```

### Task 6: Run All Tests

Run the test suite to verify everything works:

```bash
# Run all LLM module tests
pytest tests/test_llm_base.py tests/test_llm_config.py tests/test_llm_registry.py tests/test_providers.py -v

# Run existing tests to ensure backward compatibility
pytest tests/ -v --ignore=tests/test_real.py
```

## Verification

### must_haves

- [ ] MiniMaxProvider implements LLMProvider interface
- [ ] MiniMaxProvider.from_config() creates instance from ProviderConfig
- [ ] create_model() returns OpenAIChatCompletionsModel
- [ ] agent.py refactored to use provider abstraction
- [ ] Existing functionality preserved (backward compatible)
- [ ] Unit tests pass: `pytest tests/test_providers.py -v`

### Test Commands

```python
# Test provider creation
from llm import ProviderRegistry
registry = ProviderRegistry.from_env()
minimax = registry.get("minimax")
print(f"Provider: {minimax.display_name}")

# Test model creation
model = minimax.create_model()
print(f"Model type: {type(model)}")

# Test agent creation
from agent import create_agent_with_tools
agent = create_agent_with_tools(provider=minimax)
print(f"Agent: {agent.name}")
```

## Expected Output

- `llm/providers.py` with MiniMaxProvider class
- `agent.py` refactored to use provider abstraction
- `tests/test_providers.py` with unit tests
- All existing tests still pass
- No breaking changes to public API
- All unit tests pass
