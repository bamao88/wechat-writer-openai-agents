---
wave: 1
depends_on:
  - "01-PLAN.md"
files_modified:
  - llm/providers.py
  - llm/__init__.py
autonomous: true
---

# Plan 02: Implement Claude Provider

## Objective

Implement ClaudeProvider to support Claude API via third-party proxies.

## Context

Claude third-party proxies typically offer OpenAI-compatible API format. This implementation assumes OpenAI-compatible format.

## Tasks

### Task 1: Implement ClaudeProvider

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

### Task 2: Register All Providers

Update `llm/__init__.py` to register all three providers.

## Verification

### must_haves

- [ ] ClaudeProvider implements LLMProvider interface
- [ ] Works with third-party proxy (custom base_url)
- [ ] All three providers can be loaded together
