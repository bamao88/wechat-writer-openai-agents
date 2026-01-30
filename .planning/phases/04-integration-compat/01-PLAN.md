---
wave: 1
depends_on: []
files_modified:
  - tests/
  - README.md
  - .env.example
autonomous: true
---

# Plan 01: Testing and Documentation

## Objective

Add tests for the multi-provider system and update documentation.

## Tasks

### Task 1: Add Provider Tests

Create `tests/test_providers.py`:

```python
"""Tests for LLM provider abstraction."""

import pytest
from unittest.mock import patch, MagicMock

from llm import LLMConfig, ProviderRegistry, MiniMaxProvider
from llm.config import ProviderConfig


class TestLLMConfig:
    """Test configuration loading."""

    def test_load_minimax_config(self):
        """Test loading MiniMax configuration."""
        with patch.dict('os.environ', {
            'MINIMAX_API_KEY': 'test-key',
            'MINIMAX_BASE_URL': 'https://test.minimax.chat/v1',
            'MINIMAX_MODEL': 'Test-Model',
        }):
            config = LLMConfig.load_provider('minimax')
            assert config is not None
            assert config.provider_id == 'minimax'
            assert config.api_key == 'test-key'
            assert config.base_url == 'https://test.minimax.chat/v1'
            assert config.model == 'Test-Model'

    def test_load_missing_provider(self):
        """Test loading unconfigured provider returns None."""
        with patch.dict('os.environ', {}, clear=True):
            config = LLMConfig.load_provider('minimax')
            assert config is None

    def test_load_all_providers(self):
        """Test loading all configured providers."""
        with patch.dict('os.environ', {
            'MINIMAX_API_KEY': 'test-key',
            'OPENAI_API_KEY': 'test-key',
        }):
            configs = LLMConfig.load_all_providers()
            assert 'minimax' in configs
            assert 'openai' in configs
            assert 'claude' not in configs


class TestProviderRegistry:
    """Test provider registry."""

    def test_register_and_get(self):
        """Test registering and retrieving providers."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()

        registry.register('test', mock_provider)
        assert registry.get('test') == mock_provider

    def test_list_available(self):
        """Test listing available providers."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()

        registry.register('test1', mock_provider)
        registry.register('test2', mock_provider)

        available = registry.list_available()
        assert 'test1' in available
        assert 'test2' in available


class TestMiniMaxProvider:
    """Test MiniMax provider implementation."""

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
```

### Task 2: Add CLI Tests

Create `tests/test_cli.py`:

```python
"""Tests for CLI components."""

import pytest
from unittest.mock import MagicMock, patch

from cli import select_models_non_interactive
from llm import ProviderRegistry


class TestSelectModelsNonInteractive:
    """Test non-interactive model selection."""

    def test_select_single_model(self):
        """Test selecting a single model."""
        registry = ProviderRegistry()
        mock_provider = MagicMock()
        registry.register('minimax', mock_provider)

        result = select_models_non_interactive(registry, ['minimax'])
        assert result == ['minimax']

    def test_select_all(self):
        """Test selecting all models."""
        registry = ProviderRegistry()
        registry.register('minimax', MagicMock())
        registry.register('openai', MagicMock())

        result = select_models_non_interactive(registry, ['all'])
        assert set(result) == {'minimax', 'openai'}

    def test_select_invalid_model(self):
        """Test selecting invalid model raises error."""
        registry = ProviderRegistry()
        registry.register('minimax', MagicMock())

        with pytest.raises(ValueError) as exc_info:
            select_models_non_interactive(registry, ['invalid'])
        assert 'invalid' in str(exc_info.value)
```

### Task 3: Update .env.example

Create/update `.env.example`:

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

# NotebookLM Configuration
NOTEBOOK_URL=https://notebooklm.google.com/notebook/your-notebook-id
NOTEBOOK_ID=your-notebook-id

# Output Configuration
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### Task 4: Update README

Add section to README.md:

```markdown
## 多模型支持

WeChat Writer 现在支持多个 LLM Provider，可以同时使用多个模型生成文章进行对比。

### 支持的 Provider

- **MiniMax** (默认)
- **OpenAI** (支持第三方中转)
- **Claude** (支持第三方中转)

### 配置

在 `.env` 文件中配置各 Provider 的 API 密钥和设置：

```bash
# MiniMax
MINIMAX_API_KEY=your_key
MINIMAX_BASE_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-Text-01

# OpenAI (第三方中转)
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://your-proxy.com/v1
OPENAI_MODEL=gpt-4o

# Claude (第三方中转)
CLAUDE_API_KEY=your_key
CLAUDE_BASE_URL=https://your-proxy.com/v1
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 使用方法

**交互式选择模型：**
```bash
python main.py
```

**命令行指定模型：**
```bash
# 单个模型
python main.py "选题" --model minimax

# 多个模型
python main.py "选题" --model minimax --model openai

# 所有模型
python main.py "选题" --model all
```
```

## Verification

### must_haves

- [ ] Provider tests cover configuration loading
- [ ] Provider tests cover registry operations
- [ ] CLI tests cover model selection
- [ ] .env.example shows all provider configurations
- [ ] README documents multi-provider usage

### Test Commands

```bash
# Run all tests
pytest tests/test_providers.py tests/test_cli.py -v

# Run specific test
pytest tests/test_providers.py::TestLLMConfig -v
```

## Expected Output

- Test coverage for new components
- Clear documentation for users
- Example configuration file
