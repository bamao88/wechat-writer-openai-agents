---
wave: 1
depends_on: []
files_modified:
  - cli/__init__.py
  - cli/selector.py
autonomous: true
---

# Plan 01: Interactive Model Selector

## Objective

Create interactive CLI for selecting one or more models to run.

## Context

User wants to:
- Select a single model
- Select multiple models
- Run all available models
- See clear output showing which models are running

## Tasks

### Task 1: Create Selector Module

Create `cli/selector.py`:

```python
"""Interactive model selection for CLI."""

from typing import List
from llm import ProviderRegistry


def select_models(registry: ProviderRegistry) -> List[str]:
    """
    Interactive model selection.

    Returns list of selected provider IDs.
    """
    available = registry.list_available()

    if not available:
        raise ValueError("No providers configured. Check your .env file.")

    print("\n可用模型:")
    print("-" * 40)

    # Show numbered list
    for i, name in enumerate(available, 1):
        provider = registry.get(name)
        print(f"  {i}. {provider.display_name}")

    print(f"  0. 全部运行 ({len(available)} 个模型)")
    print("-" * 40)

    # Get user input
    while True:
        choice = input("\n选择模型 (输入编号，多个用逗号分隔，0=全部): ").strip()

        if not choice:
            print("请输入选择")
            continue

        if choice == "0":
            return available

        # Parse multiple selections
        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected = []
            for idx in indices:
                if idx < 1 or idx > len(available):
                    print(f"无效选择: {idx}")
                    break
                selected.append(available[idx - 1])
            else:
                return selected
        except ValueError:
            print("输入格式错误，请输入数字编号")


def select_models_non_interactive(registry: ProviderRegistry, choices: List[str]) -> List[str]:
    """
    Non-interactive model selection from command-line arguments.

    Args:
        choices: List of provider IDs (e.g., ["minimax", "openai"]) or ["all"]

    Returns:
        List of selected provider IDs
    """
    available = registry.list_available()

    if not available:
        raise ValueError("No providers configured")

    if "all" in choices:
        return available

    # Validate choices
    invalid = [c for c in choices if c not in available]
    if invalid:
        raise ValueError(f"Unknown providers: {invalid}. Available: {available}")

    return choices
```

### Task 2: Create CLI Package Init

Create `cli/__init__.py`:

```python
"""CLI utilities for multi-model runner."""

from cli.selector import select_models, select_models_non_interactive

__all__ = ["select_models", "select_models_non_interactive"]
```

## Verification

### must_haves

- [ ] Interactive selector shows all available models
- [ ] Supports single selection (1, 2, 3...)
- [ ] Supports multiple selection (1,2,3)
- [ ] Supports "all" option (0)
- [ ] Validates input and handles errors gracefully
- [ ] Non-interactive version works with command-line args

### Test Commands

```python
from llm import ProviderRegistry
from cli import select_models

# Mock test
registry = ProviderRegistry()
# ... add mock providers ...

# This would be interactive
# selected = select_models(registry)
# print(f"Selected: {selected}")
```

## Expected Output

```
可用模型:
----------------------------------------
  1. MiniMax-MiniMax-Text-01
  2. OpenAI-gpt-4o
  3. Claude-claude-3-5-sonnet-20241022
  0. 全部运行 (3 个模型)
----------------------------------------

选择模型 (输入编号，多个用逗号分隔，0=全部): 1,3
```
