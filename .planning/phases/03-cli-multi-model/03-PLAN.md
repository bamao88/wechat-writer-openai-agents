---
wave: 2
depends_on:
  - "02-PLAN.md"
files_modified:
  - main.py
autonomous: true
---

# Plan 03: Update Main Entry Point

## Objective

Update main.py to support both interactive multi-model mode and backward-compatible single-model mode.

## Context

Current main.py:
- Takes topic from command line or interactive input
- Runs single model (MiniMax)
- Needs to support model selection and multi-model execution

## Tasks

### Task 1: Update main.py

Update `main.py`:

```python
"""Main business flow for OpenAI Agent with multi-provider support."""

import os
import sys
import asyncio
import argparse
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from llm import ProviderRegistry
from cli import select_models, select_models_non_interactive, run_with_multiple_models
from main import run_workflow  # Original workflow for backward compatibility


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="WeChat Writer - Multi LLM Provider",
    )
    parser.add_argument(
        "topic",
        nargs="*",
        help="Topic to write about (if not provided, will prompt interactively)",
    )
    parser.add_argument(
        "--model", "-m",
        action="append",
        help="Model to use (can specify multiple, e.g., -m minimax -m openai). Use 'all' for all models.",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Force interactive model selection",
    )

    return parser.parse_args()


def get_topic(args) -> str:
    """Get topic from args or interactive input."""
    if args.topic:
        return " ".join(args.topic)

    topic = input("请输入选题: ").strip()
    if not topic:
        print("错误: 选题不能为空")
        sys.exit(1)
    return topic


async def main():
    """Main entry point with multi-provider support."""
    args = parse_args()

    # Get topic
    topic = get_topic(args)

    # Initialize provider registry
    registry = ProviderRegistry.from_env()

    if not registry.list_available():
        print("错误: 没有配置任何模型提供商")
        print("请检查 .env 文件中的 API 配置")
        sys.exit(1)

    # Determine model selection mode
    if args.interactive or not args.model:
        # Interactive mode
        try:
            selected_models = select_models(registry)
        except KeyboardInterrupt:
            print("\n已取消")
            sys.exit(0)
    else:
        # Command-line mode
        selected_models = select_models_non_interactive(registry, args.model)

    if not selected_models:
        print("错误: 未选择任何模型")
        sys.exit(1)

    # Run with selected models
    await run_with_multiple_models(topic, selected_models, registry)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
```

### Task 2: Handle Import Issues

Since main.py imports from itself (circular), we need to restructure. Create `workflow.py` with the original workflow functions:

Create `workflow.py`:

```python
"""Core workflow functions (extracted from main.py to avoid circular imports)."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from notebooklm_tool import run_search
from agent import create_agent_with_tools
from logger import create_trace_id


async def run_workflow(topic: str) -> Dict[str, Any]:
    """Run the complete workflow: search -> generate -> save.

    Args:
        topic: The topic to write about.

    Returns:
        Dictionary containing topic, content, trace_id, and output_path.
    """
    # Generate trace ID for this workflow
    trace_id = create_trace_id()

    # Step 1: Search for materials
    search_results = await run_search(topic)

    # Step 2: Create agent with tools
    agent = create_agent_with_tools(trace_id=trace_id)

    # Step 3: Generate article
    prompt = f"""Write an article about: {topic}

Search results to use as reference:
{search_results}

Please write a comprehensive article based on this information.
"""

    result = await run_agent(agent, prompt)
    content = result.final_output

    # Step 4: Save to file
    output_path = save_report(topic, content, trace_id)

    return {
        "topic": topic,
        "content": content,
        "trace_id": trace_id,
        "output_path": output_path,
    }


def save_report(topic: str, content: str, trace_id: str) -> str:
    """Save the generated article to a file."""
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
    filename = f"{timestamp}_{safe_topic}_{trace_id}.md"

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"**Trace ID:** {trace_id}\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        f.write(content)

    return str(filepath)


async def run_agent(agent, prompt: str):
    """Run the agent with a given prompt."""
    from agents import Runner
    result = await Runner.run(agent, prompt)
    return result
```

Then update `main.py` to import from workflow:

```python
from workflow import run_workflow
```

And update `cli/runner.py` to import from workflow:

```python
from workflow import save_report
```

## Verification

### must_haves

- [ ] main.py supports --model argument for non-interactive mode
- [ ] main.py supports -i/--interactive flag
- [ ] main.py prompts for topic if not provided as argument
- [ ] Circular import issues resolved
- [ ] All original functionality preserved

### Test Commands

```bash
# Interactive mode
python main.py

# Single model
python main.py "测试选题" --model minimax

# Multiple models
python main.py "测试选题" --model minimax --model openai

# All models
python main.py "测试选题" --model all

# Topic as argument
python main.py 测试选题
```

## Expected Output

```bash
$ python main.py "产品经理需要参与技术选型吗" --model minimax --model openai

选题: 产品经理需要参与技术选型吗
将使用 2 个模型生成文章

  [minimax] 正在生成文章...
  [openai] 正在生成文章...

============================================================
生成完成
============================================================

✅ MiniMax-MiniMax-Text-01
   文件: output/20250130_120000_产品经理_minimax_xxx.md
   耗时: 45.2s

✅ OpenAI-gpt-4o
   文件: output/20250130_120000_产品经理_openai_xxx.md
   耗时: 38.5s

============================================================
```
