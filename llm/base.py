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
