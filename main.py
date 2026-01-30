"""Main business flow for OpenAI Agent & MiniMax integration."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()

from agent import create_agent_with_tools, run_agent
from notebooklm_tool import run_search
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
    """Save the generated article to a file.

    Args:
        topic: The article topic.
        content: The article content.
        trace_id: The trace ID for tracking.

    Returns:
        Path to the saved file.
    """
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create filename with timestamp and trace_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:30])
    filename = f"{timestamp}_{safe_topic}_{trace_id}.md"

    filepath = output_dir / filename

    # Write content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"**Trace ID:** {trace_id}\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        f.write("---\n\n")
        f.write(content)

    return str(filepath)


async def main(topic: str):
    """Main entry point.
    
    Args:
        topic: The topic to write about.
    """
    print(f"选题: {topic}")
    print("正在生成文章...(预计2-3分钟)")
    print()
    
    result = await run_workflow(topic)
    
    print()
    print(f"✅ 文章已保存: {result['output_path']}")
    print(f"Trace ID: {result['trace_id']}")


if __name__ == "__main__":
    import sys
    import asyncio
    
    if len(sys.argv) > 1:
        # 从命令行参数获取选题
        topic = " ".join(sys.argv[1:])
    else:
        # 交互式输入选题
        topic = input("请输入选题: ").strip()
        if not topic:
            print("错误: 选题不能为空")
            sys.exit(1)
    
    asyncio.run(main(topic))
