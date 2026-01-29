# OpenAI Agent & MiniMax 极简开发指南

---

## 1. 核心目标

构建一个具备知识库检索能力的 Agent，要求：

| 目标 | 说明 |
|------|------|
| **极简代码** | 使用函数直连模式 |
| **高性能** | 最小化工具调用延迟 |
| **可观测** | Trace ID 全链路贯穿，解决线上不可定位问题 |

---

## 2. 技术栈

| 组件 | 依赖 | 版本要求 |
|------|------|----------|
| **Agent** | `openai-agents` | >= 0.7.0 |
| **适配层** | `litellm` | >= 1.80.15 (适配 MiniMax-M2.1) |
| **校验** | `pydantic` | >= 2.10 |
| **追踪** | 自研 `logger.py` | Trace ID 机制 |

```txt
# requirements.txt
openai-agents>=0.7.0
litellm>=1.80.15
pydantic>=2.10
python-dotenv>=1.0.0
```

---

## 3. 核心可观测性对策

必须记录并透传以下指标：

| 指标 | 说明 | 示例 |
|------|------|------|
| `trace_id` | 每次任务生成的唯一标识 | `abc-123-xyz` |
| `tool_latency` | 搜索函数执行耗时 | `0.8s` |
| `provider_latency` | LLM 响应耗时 | `1.2s` |
| `retry_count` | 异常重试次数 | `0` |
| `usage_cost` | 基于 Token 的成本核算 | `$0.012` |

```python
# logger.py 示例结构
import uuid
from datetime import datetime

def create_trace_id() -> str:
    return f"trace-{uuid.uuid4().hex[:8]}"

def log_metrics(trace_id: str, **metrics):
    print(f"[{datetime.now().isoformat()}] [{trace_id}] {metrics}")
```

---

## 相关文档

- [`project-spec.md`](./project-spec.md) - 项目规范与目录结构
- [`implementation-guide.md`](./implementation-guide.md) - 分阶段实施指南
- [`state.md`](./state.md) - 进度与状态管理
