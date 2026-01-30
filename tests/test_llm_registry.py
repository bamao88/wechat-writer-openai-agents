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
