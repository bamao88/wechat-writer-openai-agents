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
