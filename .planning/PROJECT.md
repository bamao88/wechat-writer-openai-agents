# WeChat Writer - Multi LLM Provider Support

## What This Is

一个基于 OpenAI Agents SDK 的微信公众号文章生成器。当前仅支持 MiniMax API，需要扩展支持多个 LLM Provider（OpenAI、Claude 等），并通过命令行交互实现灵活选择模型运行。

## Core Value

用户可以通过简单的命令行交互，选择一个或多个模型为同一选题生成文章，方便对比不同模型的输出质量。

## Requirements

### Validated

- ✓ 基于 OpenAI Agents SDK 的 Agent 架构 — existing
- ✓ MiniMax API 集成 — existing
- ✓ 文章搜索和生成工作流 — existing
- ✓ 文章保存到本地文件 — existing

### Active

- [ ] 抽象 LLM Provider 接口，支持多 Provider 扩展
- [ ] 支持 OpenAI API（第三方中转）
- [ ] 支持 Claude API（第三方中转）
- [ ] 命令行交互式模型选择
- [ ] 支持同时运行多个模型对比
- [ ] 配置管理（.env 多 Provider 配置）

### Out of Scope

- Web UI 界面 — 保持 CLI 工具定位
- 模型输出自动对比/评分 — 用户自行对比
- 支持非 OpenAI 兼容格式的 API — 仅支持 OpenAI 兼容格式
- 实时流式输出 — 保持现有批量生成模式

## Context

- 现有代码使用 `openai-agents` SDK 和 MiniMax API
- MiniMax 使用 OpenAI 兼容格式（base_url + api_key）
- 用户的 OpenAI/Claude 都是第三方中转服务，需要提供自定义 base_url
- 需要保持向后兼容，现有功能不受影响

## Constraints

- **Tech stack**: Python, openai-agents SDK, OpenAI 兼容 API
- **Compatibility**: 保持现有 main.py 接口可用
- **Configuration**: 使用 .env 文件管理多 Provider 配置
- **CLI**: 使用内置 input 或简单库实现交互，避免过重依赖

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 使用 Provider 抽象模式 | 统一接口，便于扩展新模型 | — Pending |
| 保持 .env 配置方式 | 与现有项目一致，用户熟悉 | — Pending |
| 内置 input 实现交互 | 避免额外依赖，保持轻量 | — Pending |

---
*Last updated: 2025-01-30 after initialization*
