"""
Mini Writer Agent - 工具定义层
负责 import 并调用各种工具函数
"""
import os
from datetime import datetime
from notebooklm_tool import search_notebooklm


def search_materials(topic: str) -> str:
    """
    搜索背景资料
    
    Args:
        topic: 搜索主题
        
    Returns:
        搜索到的背景资料文本
    """
    print(f"[Tools] 搜索主题: {topic}")
    
    # 调用 NotebookLM 搜索工具
    results = search_notebooklm(topic)
    
    if not results:
        return "暂无相关背景资料"
    
    return results


def save_article(topic: str, content: str) -> str:
    """
    保存生成的文章
    
    Args:
        topic: 文章主题
        content: 文章内容
        
    Returns:
        保存的文件路径
    """
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in " _-")[:30]
    filename = f"{timestamp}_{safe_topic}.md"
    filepath = os.path.join(output_dir, filename)
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(content)
    
    print(f"[Tools] 文章已保存: {filepath}")
    return filepath


def update_state(status: str, message: str) -> None:
    """
    更新状态文件
    
    Args:
        status: 状态标识
        message: 状态消息
    """
    doc_dir = os.getenv("DOC_DIR", "./doc")
    state_file = os.path.join(doc_dir, "state.md")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"- [{timestamp}] **{status}**: {message}\n"
    
    with open(state_file, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"[Tools] 状态已更新: {status}")
