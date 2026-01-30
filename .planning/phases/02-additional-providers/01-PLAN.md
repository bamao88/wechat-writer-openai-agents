---
wave: 1
depends_on: []
files_modified:
  - llm/providers.py
  - llm/__init__.py
autonomous: true
---

# Plan 01: Implement OpenAI Provider

## Objective

Implement OpenAIProvider to support OpenAI API and third-party proxies.

## Context

OpenAI uses standard OpenAI API format. Many third-party proxies also use this format.

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

### Task 2: Register Provider

Update `llm/__init__.py` to register OpenAIProvider.

## Verification

### must_haves

- [ ] OpenAIProvider implements LLMProvider interface
- [ ] Works with third-party proxy (custom base_url)
- [ ] ProviderRegistry can load it from env
