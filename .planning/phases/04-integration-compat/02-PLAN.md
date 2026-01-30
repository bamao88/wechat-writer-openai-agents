---
wave: 2
depends_on:
  - "01-PLAN.md"
files_modified:
  - main.py
  - agent.py
autonomous: true
---

# Plan 02: Backward Compatibility

## Objective

Ensure existing functionality works unchanged for users who don't want to use multi-provider features.

## Context

Current usage:
```bash
python main.py "选题"
```

This should continue to work exactly as before.

## Tasks

### Task 1: Preserve Original Behavior

Update `main.py` to detect when to use new multi-mode vs old single-mode:

```python
"""Main entry point with backward compatibility."""

import os
import sys
import asyncio
import argparse
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from llm import ProviderRegistry
from cli import select_models, select_models_non_interactive, run_with_multiple_models
from workflow import run_workflow


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WeChat Writer - Multi LLM Provider",
    )
    parser.add_argument(
        "topic",
        nargs="*",
        help="Topic to write about",
    )
    parser.add_argument(
        "--model", "-m",
        action="append",
        dest="models",
        help="Model to use (can specify multiple). Use 'all' for all models.",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Force interactive model selection",
    )

    return parser.parse_args()


def get_topic(args) -> Optional[str]:
    """Get topic from args or return None."""
    if args.topic:
        return " ".join(args.topic)
    return None


async def run_single_model_mode(topic: str):
    """Original single-model mode for backward compatibility."""
    print(f"选题: {topic}")
    print("正在生成文章...(预计2-3分钟)")
    print()

    result = await run_workflow(topic)

    print()
    print(f"✅ 文章已保存: {result['output_path']}")
    print(f"Trace ID: {result['trace_id']}")


async def run_multi_model_mode(topic: str, models: List[str], registry: ProviderRegistry):
    """New multi-model mode."""
    await run_with_multiple_models(topic, models, registry)


async def main():
    """Main entry point."""
    args = parse_args()

    # Get topic
    topic = get_topic(args)
    if topic is None:
        topic = input("请输入选题: ").strip()
        if not topic:
            print("错误: 选题不能为空")
            sys.exit(1)

    # Initialize registry
    registry = ProviderRegistry.from_env()

    if not registry.list_available():
        print("错误: 没有配置任何模型提供商")
        sys.exit(1)

    # Determine mode
    if args.models or args.interactive:
        # Multi-model mode
        if args.interactive or not args.models:
            selected_models = select_models(registry)
        else:
            selected_models = select_models_non_interactive(registry, args.models)

        if not selected_models:
            print("错误: 未选择任何模型")
            sys.exit(1)

        await run_multi_model_mode(topic, selected_models, registry)
    else:
        # Backward compatibility: single model mode
        # Only works if minimax is configured
        if "minimax" not in registry.list_available():
            print("错误: MiniMax 未配置，请使用 --model 指定模型")
            print(f"可用模型: {', '.join(registry.list_available())}")
            sys.exit(1)

        await run_single_model_mode(topic)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
```

### Task 2: Ensure Agent Compatibility

Verify `agent.py` exports work correctly:

```python
# agent.py should export both old and new functions
__all__ = [
    "create_agent",
    "create_agent_with_tools",
    "create_agent_with_provider",  # New
    "run_agent",
]
```

## Verification

### must_haves

- [ ] `python main.py "选题"` works exactly as before
- [ ] Uses MiniMax by default when no --model specified
- [ ] Shows helpful error if MiniMax not configured
- [ ] New flags don't break existing scripts

### Test Commands

```bash
# Original usage (should work unchanged)
python main.py "产品经理需要参与技术选型吗"

# With explicit topic argument
python main.py 产品经理需要参与技术选型吗

# New multi-model usage
python main.py "选题" --model all
```

## Expected Output

Original behavior preserved:
```
$ python main.py "测试选题"
选题: 测试选题
正在生成文章...(预计2-3分钟)

...

✅ 文章已保存: output/20250130_120000_测试选题_xxx.md
Trace ID: xxx
```
