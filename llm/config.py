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
