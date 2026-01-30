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
