# 项目初始化与状态管理规范

> 本规范定义了项目的物理结构、进度追踪方式以及产出物管理规则。

---

## 1. 最终项目目录结构 (直连版)

为了实现高性能"直连"，背景代码必须处在 Python 能够直接 `import` 的位置。

```
wechat-writer-openai-agents/
├── .env                # 环境变量配置
├── requirements.txt    # 项目依赖清单
├── main.py             # 业务执行入口 (Trace ID 生成)
├── agent.py            # Agent 大脑逻辑 (加载 prompts/ 下的提示词)
├── tools.py            # 工具定义层 (工具耗时采集)
├── notebooklm_tool.py  # NotebookLM 搜索工具 (集成 PleasePrompto/notebooklm-skill)
├── notebooklm_skill/   # [Git Submodule] NotebookLM Skill 仓库
│   └── scripts/
│       ├── run.py           # 脚本包装器
│       ├── auth_manager.py  # 认证管理
│       ├── notebook_manager.py  # 笔记本管理
│       └── ask_question.py  # 查询接口
├── logger.py           # 统一日志与追踪模块 (支持 Trace ID 并写入 logs/)
├── doc/                # 文档目录
│   ├── project-spec.md    # 项目规范与目录结构
│   ├── state.md           # 进度与状态管理
│   └── implementation-guide.md  # 分阶段实施指南
├── prompts/            # [New] 提示词目录 (版本管理，如 writer_v1.txt)
├── logs/               # [New] 日志目录 (存放持久化 Trace 日志)
├── output/             # 生成的文章与 Trace 报告 (JSON)
└── tests/              # 测试脚本目录
    ├── conftest.py          # Pytest 配置与路径设置
    ├── test_imports.py      # 依赖导入验证测试
    ├── test_logger.py       # Trace ID 生成测试
    ├── test_minimax_connection.py  # MiniMax 连接测试
    ├── test_notebooklm.py   # NotebookLM 搜索工具测试
    ├── test_tools.py        # 工具层与耗时采集测试
    ├── test_agent_tools.py  # Agent 工具挂载测试
    ├── test_main.py         # 主业务流程测试
    └── test_real.py         # 端到端真实 API 测试
```

---

## 2. 状态管理逻辑 (`doc/state.md`)

| 状态 | 英文 | 说明 |
|------|------|------|
| 🔄 进行中 | `In Progress` | 正在编写或调试 |
| ✅ 已完成 | `Done` | 已通过 `test_real.py` 验证的任务 |

---

## 3. 产出物管理规范 (`output/`)

| 配置项 | 值 |
|--------|-----|
| **路径** | `./output/` |
| **命名规范** | `YYYYMMDD_主题名称_文章.md` |

**示例**：

```
output/
├── 20260129_AI技术趋势_文章.md
├── 20260130_量子计算入门_文章.md
└── ...
```

---

## 4. 核心模块说明

| 模块 | 功能 | 关键函数/类 |
|------|------|-------------|
| `logger.py` | Trace ID 生成 | `create_trace_id()` |
| `agent.py` | Agent 工厂 | `create_agent()`, `create_agent_with_tools()`, `run_agent()` |
| `notebooklm_tool.py` | 搜索工具（集成 Skill） | `run_search()`, `setup_authentication()`, `list_notebooks()` |
| `notebooklm_skill/` | NotebookLM Skill | `auth_manager.py`, `notebook_manager.py`, `ask_question.py` |
| `tools.py` | 工具层 | `wrap_tool_with_latency()`, `get_registered_tools()`, `search_materials` |
| `main.py` | 业务流程 | `run_workflow()`, `save_report()` |

---

## 5. 快速启动建议

```bash
# Step 1: 创建文件夹
mkdir -p doc output tests logs prompts

# Step 2: 克隆 NotebookLM Skill（如尚未克隆）
git clone --depth 1 https://github.com/PleasePrompto/notebooklm-skill.git notebooklm_skill

# Step 3: 安装依赖
pip install -r requirements.txt

# Step 4: 运行测试
pytest tests/ -v --ignore=tests/test_real.py

# Step 5: 配置 NotebookLM 认证（一次性）
python notebooklm_skill/scripts/run.py auth_manager.py setup

# Step 6: 配置 MiniMax API Key 后运行真实 API 测试
# 在 .env 文件中配置 MINIMAX_API_KEY
pytest tests/test_real.py -v
```

---

## 6. 测试覆盖

| 测试文件 | 测试内容 | 测试数量 |
|----------|----------|----------|
| `test_imports.py` | 依赖可导入性 | 5 |
| `test_logger.py` | Trace ID 格式与唯一性 | 5 |
| `test_minimax_connection.py` | Agent 创建与连接 | 6 |
| `test_notebooklm.py` | NotebookLM Skill 集成测试 | 10 |
| `test_tools.py` | 工具层与耗时采集 | 7 |
| `test_agent_tools.py` | 工具挂载与调用 | 6 |
| `test_main.py` | 主业务流程 | 7 |
| `test_real.py` | 端到端真实 API 测试 | 5 |

**总计**: 45+ 单元测试，覆盖所有核心功能

---

## 相关文档

- [`implementation-guide.md`](./implementation-guide.md) - 分阶段实施指南
- [`state.md`](./state.md) - 进度与状态管理
