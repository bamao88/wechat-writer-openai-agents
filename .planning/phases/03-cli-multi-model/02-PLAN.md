---
wave: 1
depends_on:
  - "01-PLAN.md"
files_modified:
  - cli/runner.py
  - cli/__init__.py
autonomous: true
---

# Plan 02: Multi-Model Runner

## Objective

Implement runner that executes the same topic across multiple models sequentially.

## Context

Need to run the same workflow (search -> generate -> save) for each selected model, collecting results.

## Tasks

### Task 1: Create Runner Module

Create `cli/runner.py`:

```python
"""Multi-model runner for executing workflows across multiple providers."""

import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from llm import ProviderRegistry
from agent import create_agent_with_provider
from notebooklm_tool import run_search
from logger import create_trace_id


async def run_single_model(
    topic: str,
    provider_name: str,
    registry: ProviderRegistry,
) -> Dict[str, Any]:
    """
    Run workflow with a single model.

    Returns:
        Dict with keys: topic, content, trace_id, output_path, provider, duration
    """
    from main import save_report

    provider = registry.get(provider_name)
    trace_id = create_trace_id()

    print(f"  [{provider_name}] 正在生成文章...")
    start_time = datetime.now()

    try:
        # Step 1: Search (shared across models, could be cached)
        search_results = await run_search(topic)

        # Step 2: Create agent with this provider
        agent = create_agent_with_provider(provider, trace_id=trace_id)

        # Step 3: Generate article
        prompt = f"""Write an article about: {topic}

Search results to use as reference:
{search_results}

Please write a comprehensive article based on this information.
"""

        from agents import Runner
        result = await Runner.run(agent, prompt)
        content = result.final_output

        # Step 4: Save with provider name in filename
        output_path = save_report_with_provider(topic, content, trace_id, provider_name)

        duration = (datetime.now() - start_time).total_seconds()

        return {
            "topic": topic,
            "content": content,
            "trace_id": trace_id,
            "output_path": output_path,
            "provider": provider_name,
            "display_name": provider.display_name,
            "duration": duration,
            "success": True,
            "error": None,
        }

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        return {
            "topic": topic,
            "content": None,
            "trace_id": trace_id,
            "output_path": None,
            "provider": provider_name,
            "display_name": provider.display_name if provider else provider_name,
            "duration": duration,
            "success": False,
            "error": str(e),
        }


def save_report_with_provider(
    topic: str,
    content: str,
    trace_id: str,
    provider_name: str,
) -> str:
    """Save report with provider name in filename."""
    import os

    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
    filename = f"{timestamp}_{safe_topic}_{provider_name}_{trace_id}.md"

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"**模型:** {provider_name}\n\n")
        f.write(f"**Trace ID:** {trace_id}\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        f.write(content)

    return str(filepath)


async def run_with_multiple_models(
    topic: str,
    model_names: List[str],
    registry: ProviderRegistry,
) -> Dict[str, Any]:
    """
    Run workflow with multiple models sequentially.

    Args:
        topic: The topic to write about
        model_names: List of provider names to use
        registry: Provider registry

    Returns:
        Dict with results for each model and summary
    """
    print(f"\n选题: {topic}")
    print(f"将使用 {len(model_names)} 个模型生成文章\n")

    results = []
    for name in model_names:
        result = await run_single_model(topic, name, registry)
        results.append(result)

    # Print summary
    print("\n" + "=" * 60)
    print("生成完成")
    print("=" * 60)

    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"\n{status} {r['display_name']}")
        if r["success"]:
            print(f"   文件: {r['output_path']}")
            print(f"   耗时: {r['duration']:.1f}s")
        else:
            print(f"   错误: {r['error']}")

    print("\n" + "=" * 60)

    return {
        "topic": topic,
        "models": model_names,
        "results": {r["provider"]: r for r in results},
        "total": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
    }
```

### Task 2: Update CLI Init

Update `cli/__init__.py`:

```python
"""CLI utilities for multi-model runner."""

from cli.selector import select_models, select_models_non_interactive
from cli.runner import run_with_multiple_models, run_single_model

__all__ = [
    "select_models",
    "select_models_non_interactive",
    "run_with_multiple_models",
    "run_single_model",
]
```

## Verification

### must_haves

- [ ] Runner executes each model sequentially
- [ ] Each result saved with provider name in filename
- [ ] Summary shows all results with status
- [ ] Errors handled gracefully (one failure doesn't stop others)
- [ ] Duration tracked for each model

### Test Commands

```python
from cli.runner import run_with_multiple_models
from llm import ProviderRegistry

async def test():
    registry = ProviderRegistry.from_env()
    result = await run_with_multiple_models(
        topic="测试选题",
        model_names=["minimax"],
        registry=registry
    )
    print(result)

asyncio.run(test())
```

## Expected Output

```
选题: 测试选题
将使用 1 个模型生成文章

  [minimax] 正在生成文章...

============================================================
生成完成
============================================================

✅ MiniMax-MiniMax-Text-01
   文件: output/20250130_120000_测试选题_minimax_xxx.md
   耗时: 45.2s

============================================================
```
