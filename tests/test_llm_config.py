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
