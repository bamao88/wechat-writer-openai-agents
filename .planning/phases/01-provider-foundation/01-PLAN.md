---
wave: 1
depends_on: []
files_modified:
  - llm/__init__.py
  - llm/base.py
  - llm/config.py
  - llm/registry.py
  - tests/test_llm_base.py
  - tests/test_llm_config.py
  - tests/test_llm_registry.py
autonomous: true
must_haves:
  - llm/base.py defines LLMProvider abstract class with create_model() and config property
  - llm/config.py loads provider configs from environment variables
  - llm/registry.py can register and retrieve providers
  - ProviderRegistry.from_env() loads all configured providers
  - Configuration validation raises clear errors for missing required fields
  - Unit tests pass for base, config, and registry modules
---

# Plan 01: Provider Abstraction and Configuration

## Objective

Create the foundational Provider abstraction layer including base class, configuration system, and registry.

## Context

Current code in `agent.py` directly creates MiniMax client:
```python
def _get_minimax_model():
    api_key = os.getenv("MINIMAX_API_KEY")
    client = AsyncOpenAI(api_key=api_key, base_url="...")
    return OpenAIChatCompletionsModel(model="MiniMax-Text-01", openai_client=client)
```

We need to abstract this so multiple providers can be supported.

## Tasks

### Task 1: Create Provider Base Class

Create `llm/base.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ModelConfig:
    name: str           # Display name, e.g., "MiniMax-Text-01"
    provider: str       # Provider ID, e.g., "minimax"
    model_id: str       # Model identifier for API
    api_key: str
    base_url: str

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def create_model(self) -> Any:
        """Create and return a model instance compatible with OpenAI Agents SDK."""
        pass

    @property
    @abstractmethod
    def config(self) -> ModelConfig:
        """Return the provider's configuration."""
        pass

    @property
    def display_name(self) -> str:
        """Return human-readable name for CLI display."""
        return f"{self.config.provider.upper()}-{self.config.model_id}"
```

### Task 2: Create Configuration System

Create `llm/config.py`:

```python
import os
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    provider_id: str
    api_key: str
    base_url: str
    model: str
    enabled: bool = True

class LLMConfig:
    """Manages LLM provider configurations from environment."""

    # Provider configuration schema
    PROVIDERS = {
        "minimax": {
            "api_key_var": "MINIMAX_API_KEY",
            "base_url_var": "MINIMAX_BASE_URL",
            "model_var": "MINIMAX_MODEL",
            "default_base_url": "https://api.minimax.chat/v1",
            "default_model": "MiniMax-Text-01",
        },
        "openai": {
            "api_key_var": "OPENAI_API_KEY",
            "base_url_var": "OPENAI_BASE_URL",
            "model_var": "OPENAI_MODEL",
            "default_base_url": "https://api.openai.com/v1",
            "default_model": "gpt-4o",
        },
        "claude": {
            "api_key_var": "CLAUDE_API_KEY",
            "base_url_var": "CLAUDE_BASE_URL",
            "model_var": "CLAUDE_MODEL",
            "default_base_url": None,  # Must be provided for third-party proxy
            "default_model": "claude-3-5-sonnet-20241022",
        },
    }

    @classmethod
    def load_provider(cls, provider_id: str) -> Optional[ProviderConfig]:
        """Load configuration for a single provider."""
        schema = cls.PROVIDERS.get(provider_id)
        if not schema:
            return None

        api_key = os.getenv(schema["api_key_var"])
        if not api_key:
            return None  # Provider not configured

        base_url = os.getenv(schema["base_url_var"], schema["default_base_url"])
        model = os.getenv(schema["model_var"], schema["default_model"])

        if not base_url:
            raise ValueError(f"{provider_id}: base_url required but not provided")

        return ProviderConfig(
            provider_id=provider_id,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

    @classmethod
    def load_all_providers(cls) -> Dict[str, ProviderConfig]:
        """Load all configured providers."""
        configs = {}
        for provider_id in cls.PROVIDERS:
            config = cls.load_provider(provider_id)
            if config:
                configs[provider_id] = config
        return configs
```

### Task 3: Create Provider Registry

Create `llm/registry.py`:

```python
from typing import Dict, List, Optional, Type
from llm.base import LLMProvider, ModelConfig
from llm.config import LLMConfig, ProviderConfig

class ProviderRegistry:
    """Registry for managing LLM provider instances."""

    _providers: Dict[str, LLMProvider] = {}
    _provider_classes: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register_class(cls, provider_id: str, provider_class: Type[LLMProvider]):
        """Register a provider class."""
        cls._provider_classes[provider_id] = provider_class

    @classmethod
    def register(cls, name: str, provider: LLMProvider) -> None:
        """Register a provider instance."""
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str) -> Optional[LLMProvider]:
        """Get a provider by name."""
        return cls._providers.get(name)

    @classmethod
    def list_available(cls) -> List[str]:
        """Return list of available provider names."""
        return list(cls._providers.keys())

    @classmethod
    def from_env(cls) -> "ProviderRegistry":
        """Create registry from environment configuration."""
        registry = cls()
        registry._providers = {}

        # Load all configured providers
        configs = LLMConfig.load_all_providers()

        for provider_id, config in configs.items():
            provider_class = cls._provider_classes.get(provider_id)
            if provider_class:
                provider = provider_class.from_config(config)
                registry.register(provider_id, provider)

        return registry

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, name: str) -> bool:
        return name in self._providers
```

### Task 4: Create Package Init

Create `llm/__init__.py`:

```python
from llm.base import LLMProvider, ModelConfig
from llm.config import LLMConfig, ProviderConfig
from llm.registry import ProviderRegistry

__all__ = [
    "LLMProvider",
    "ModelConfig",
    "LLMConfig",
    "ProviderConfig",
    "ProviderRegistry",
]
```

### Task 5: Create Unit Tests

Create `tests/test_llm_base.py`:

```python
"""Tests for LLM base classes."""

import pytest
from abc import ABC
from llm.base import LLMProvider, ModelConfig


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_creation(self):
        """Test ModelConfig can be created."""
        config = ModelConfig(
            name="Test-Model",
            provider="test",
            model_id="model-1",
            api_key="test-key",
            base_url="https://test.com",
        )
        assert config.name == "Test-Model"
        assert config.provider == "test"
        assert config.model_id == "model-1"


class TestLLMProvider:
    """Test LLMProvider abstract base class."""

    def test_is_abstract(self):
        """Test LLMProvider is abstract."""
        assert issubclass(LLMProvider, ABC)

    def test_cannot_instantiate_directly(self):
        """Test LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()
```

Create `tests/test_llm_config.py`:

```python
"""Tests for LLM configuration."""

import pytest
from unittest.mock import patch

from llm.config import LLMConfig, ProviderConfig


class TestProviderConfig:
    """Test ProviderConfig dataclass."""

    def test_creation(self):
        """Test ProviderConfig can be created."""
        config = ProviderConfig(
            provider_id="test",
            api_key="key",
            base_url="https://test.com",
            model="model-1",
        )
        assert config.provider_id == "test"
        assert config.enabled is True  # default


class TestLLMConfig:
    """Test LLMConfig class."""

    def test_load_minimax_config(self):
        """Test loading MiniMax configuration."""
        with patch.dict('os.environ', {
            'MINIMAX_API_KEY': 'test-key',
            'MINIMAX_BASE_URL': 'https://test.minimax.chat/v1',
            'MINIMAX_MODEL': 'Test-Model',
        }, clear=True):
            config = LLMConfig.load_provider('minimax')
            assert config is not None
            assert config.provider_id == 'minimax'
            assert config.api_key == 'test-key'

    def test_load_missing_provider_returns_none(self):
        """Test loading unconfigured provider returns None."""
        with patch.dict('os.environ', {}, clear=True):
            config = LLMConfig.load_provider('minimax')
            assert config is None

    def test_load_all_providers(self):
        """Test loading all configured providers."""
        with patch.dict('os.environ', {
            'MINIMAX_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
        }, clear=True):
            configs = LLMConfig.load_all_providers()
            assert 'minimax' in configs
            assert 'openai' in configs
            assert 'claude' not in configs
```

Create `tests/test_llm_registry.py`:

```python
"""Tests for ProviderRegistry."""

import pytest
from unittest.mock import MagicMock, patch

from llm.registry import ProviderRegistry
from llm.base import LLMProvider


class TestProviderRegistry:
    """Test ProviderRegistry functionality."""

    def test_register_and_get(self):
        """Test registering and retrieving providers."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()

        registry.register('test', mock_provider)
        assert registry.get('test') == mock_provider

    def test_list_available(self):
        """Test listing available providers."""
        registry = ProviderRegistry()

        registry.register('test1', MagicMock())
        registry.register('test2', MagicMock())

        available = registry.list_available()
        assert 'test1' in available
        assert 'test2' in available

    def test_contains(self):
        """Test __contains__ method."""
        registry = ProviderRegistry()
        registry.register('test', MagicMock())

        assert 'test' in registry
        assert 'missing' not in registry

    def test_len(self):
        """Test __len__ method."""
        registry = ProviderRegistry()
        assert len(registry) == 0

        registry.register('test', MagicMock())
        assert len(registry) == 1
```

### Task 6: Update .env.example

Add to `.env.example` (create if not exists):

```bash
# MiniMax Configuration
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01

# OpenAI Configuration (支持第三方中转)
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://your-openai-proxy.com/v1
OPENAI_MODEL=gpt-4o

# Claude Configuration (支持第三方中转)
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_BASE_URL=https://your-claude-proxy.com/v1
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## Verification

### must_haves

- [ ] `llm/base.py` defines `LLMProvider` abstract class with `create_model()` and `config` property
- [ ] `llm/config.py` loads provider configs from environment variables
- [ ] `llm/registry.py` can register and retrieve providers
- [ ] `ProviderRegistry.from_env()` loads all configured providers
- [ ] Configuration validation raises clear errors for missing required fields
- [ ] Unit tests pass: `pytest tests/test_llm_base.py tests/test_llm_config.py tests/test_llm_registry.py -v`

### Test Commands

```python
# Test configuration loading
from llm.config import LLMConfig
configs = LLMConfig.load_all_providers()
print(f"Loaded {len(configs)} providers")

# Test registry
from llm.registry import ProviderRegistry
registry = ProviderRegistry.from_env()
print(f"Available: {registry.list_available()}")
```

## Expected Output

- Directory structure:
  ```
  llm/
  ├── __init__.py
  ├── base.py
  ├── config.py
  └── registry.py
  ```
- All imports work without errors
- Configuration loads correctly from .env
- All unit tests pass
