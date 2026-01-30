---
wave: 2
depends_on:
  - "02-PLAN.md"
files_modified:
  - llm/providers.py
  - llm/__init__.py
autonomous: true
---

# Plan 03: OpenAI and Claude Providers

## Objective

Implement OpenAIProvider and ClaudeProvider to support third-party API proxies.

## Context

Both OpenAI and Claude (via third-party proxy) use OpenAI-compatible API format. The main differences are:
- Different environment variable names
- Different default base URLs
- Different model names

## Tasks

### Task 1: Implement OpenAIProvider

Add to `llm/providers.py`:

```python
class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation (supports third-party proxies)."""

    def __init__(self, config: ModelConfig):
        self._config = config
        self._client = None
        self._model = None

    @classmethod
    def from_config(cls, config: ProviderConfig) -> "OpenAIProvider":
        """Create provider from configuration."""
        model_config = ModelConfig(
            name=f"OpenAI-{config.model}",
            provider="openai",
            model_id=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        return cls(model_config)

    def create_model(self) -> OpenAIChatCompletionsModel:
        """Create OpenAI model instance."""
        if self._model is None:
            self._client = AsyncOpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
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
        return f"OpenAI-{self._config.model_id}"
```

### Task 2: Implement ClaudeProvider

Add to `llm/providers.py`:

```python
class ClaudeProvider(LLMProvider):
    """Claude API provider implementation (supports third-party proxies with OpenAI-compatible format)."""

    def __init__(self, config: ModelConfig):
        self._config = config
        self._client = None
        self._model = None

    @classmethod
    def from_config(cls, config: ProviderConfig) -> "ClaudeProvider":
        """Create provider from configuration."""
        model_config = ModelConfig(
            name=f"Claude-{config.model}",
            provider="claude",
            model_id=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        return cls(model_config)

    def create_model(self) -> OpenAIChatCompletionsModel:
        """Create Claude model instance via OpenAI-compatible API."""
        if self._model is None:
            self._client = AsyncOpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
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
        return f"Claude-{self._config.model_id}"
```

### Task 3: Register All Providers

Update `llm/__init__.py`:

```python
from llm.base import LLMProvider, ModelConfig
from llm.config import LLMConfig, ProviderConfig
from llm.registry import ProviderRegistry
from llm.providers import MiniMaxProvider, OpenAIProvider, ClaudeProvider

# Register provider classes
ProviderRegistry.register_class("minimax", MiniMaxProvider)
ProviderRegistry.register_class("openai", OpenAIProvider)
ProviderRegistry.register_class("claude", ClaudeProvider)

__all__ = [
    "LLMProvider",
    "ModelConfig",
    "LLMConfig",
    "ProviderConfig",
    "ProviderRegistry",
    "MiniMaxProvider",
    "OpenAIProvider",
    "ClaudeProvider",
]
```

### Task 4: Update .env Configuration

Ensure `.env` file has all three providers configured:

```bash
# MiniMax Configuration
MINIMAX_API_KEY=sk-api-L3iZgi1P0IVe-zxQ3C33KBcXujiOzIpfAQkWvWt5oYtwIGG9UoZ5D3UEeKxJcZDBSUNokyAumfkFQqei_zkoHiZs0edugOgNhrjK0J5R3fMx_yxNS4M2HVQ
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01

# OpenAI Configuration (第三方中转)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://your-openai-proxy.com/v1
OPENAI_MODEL=gpt-4o

# Claude Configuration (第三方中转)
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_BASE_URL=https://your-claude-proxy.com/v1
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## Verification

### must_haves

- [ ] OpenAIProvider implements LLMProvider interface
- [ ] ClaudeProvider implements LLMProvider interface
- [ ] Both providers can be registered in ProviderRegistry
- [ ] ProviderRegistry.from_env() loads all three providers when configured
- [ ] Each provider creates correct model instance

### Test Commands

```python
# Test all providers
from llm import ProviderRegistry

registry = ProviderRegistry.from_env()
print(f"Available providers: {registry.list_available()}")

for name in registry.list_available():
    provider = registry.get(name)
    print(f"\n{name}:")
    print(f"  Display: {provider.display_name}")
    print(f"  Model ID: {provider.config.model_id}")
    print(f"  Base URL: {provider.config.base_url}")
```

## Expected Output

- All three providers implemented in `llm/providers.py`
- ProviderRegistry can load any combination of configured providers
- Each provider creates functional model instance
