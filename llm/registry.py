from typing import Dict, List, Optional, Type
from llm.base import LLMProvider, ModelConfig
from llm.config import LLMConfig, ProviderConfig


class ProviderRegistry:
    """Registry for managing LLM provider instances."""

    _provider_classes: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register_class(cls, provider_id: str, provider_class: Type[LLMProvider]):
        """Register a provider class."""
        cls._provider_classes[provider_id] = provider_class

    def __init__(self):
        """Initialize a new registry instance."""
        self._providers: Dict[str, LLMProvider] = {}

    def register(self, name: str, provider: LLMProvider) -> None:
        """Register a provider instance."""
        self._providers[name] = provider

    def get(self, name: str) -> Optional[LLMProvider]:
        """Get a provider by name."""
        return self._providers.get(name)

    def list_available(self) -> List[str]:
        """Return list of available provider names."""
        return list(self._providers.keys())

    @classmethod
    def from_env(cls) -> "ProviderRegistry":
        """Create registry from environment configuration."""
        registry = cls()

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
