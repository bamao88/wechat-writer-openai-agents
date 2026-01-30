# AGENTS.md

## 命令
- **生成文章**: `python main.py "你的选题"` 或直接 `python main.py` 然后输入选题
- 运行所有测试: `pytest tests/`
- 运行单个测试: `pytest tests/test_file.py::test_function -v`
- 带异步超时运行: `pytest --timeout=30`

## 架构
- **agent.py**: 通过 OpenAI 兼容 API 创建 MiniMax LLM Agent
- **main.py**: 编排工作流: 搜索 → 生成 → 保存到 `output/`
- **tools.py**: 使用 `@function_tool` 装饰器的 Agent 工具，包含延迟追踪
- **notebooklm_tool.py**: 通过 Patchright 集成 NotebookLM 搜索
- **prompts/**: 提示词模板 (如 `writer_v1.txt`)
- **tests/**: pytest + pytest-asyncio 测试

## 代码风格
- Python 3.10+，全程使用 async/await 模式
- 必须使用类型提示: `from typing import Dict, Any, Optional, List`
- 文件路径使用 `pathlib.Path`
- 文档字符串: Google 风格，包含 Args/Returns 部分
- 环境变量通过 `os.getenv()` 获取，API 密钥存放在 `.env`
- 工具必须是异步的，并使用 `agents` 的 `@function_tool` 装饰器
- 错误处理: 让异常传播，使用 try/finally 进行清理
