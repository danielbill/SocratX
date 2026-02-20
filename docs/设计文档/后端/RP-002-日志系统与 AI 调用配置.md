# RP-002 设计：日志系统与 AI 调用配置

**创建日期**: 2026 年 2 月 20 日
**状态**: 待确认

---

## 需求分析

### 目标
完成一次完整的 AI 对话流程：
1. 配置 GLM-4.7 AI 调用
2. 用户输入"你好"
3. 注入系统提示
4. AI 回复"你好，我是 SocratX"

### 新增需求
1. **统一日志系统**: 后台统一使用单例 logger
2. **三个日志文件**:
   - `SocratX.log` - 系统及系统信息
   - `conversation.log` - 通话内容
   - `ai.log` - 云端 AI 信息

---

## 设计方案

### 1. 日志系统设计

**文件**: `services/agent/utils/logger.py`

```python
from utils.logger import logger

# 1. 系统日志 → logs/SocratX.log
logger.system("SocratX Agent API started")

# 2. 对话日志 → logs/conversation.log
logger.conversation(session_id="default", role="USER", content="你好")
logger.conversation(session_id="default", role="AI", content="你好，我是 SocratX")

# 3. AI 交互日志 → logs/ai.log
logger.ai_request(model="glm-4", messages=[...])
logger.ai_response(content="你好，我是 SocratX", usage={"total_tokens": 100})
```

**日志格式**:
- `SocratX.log`: `[2026-02-20 10:30:00] [INFO] SocratX Agent API started`
- `conversation.log`: `[2026-02-20 10:30:00] [SESSION:default] [USER] 你好`
- `ai.log`: `[2026-02-20 10:30:00] [REQUEST] Model: glm-4 | Messages: [...]`

### 2. AI 调用配置

#### 2.1 配置文件
**文件**: `services/agent/.env` 或 `config.yaml`

```yaml
providers:
  default_provider: "zhipu"  # 智谱 AI
  zhipu_api_key: "your_api_key"
  
agent:
  model: "glm-4"  # GLM-4.7 对应模型名
  temperature: 0.7
  max_tokens: 4096
```

#### 2.2 LiteLLM 配置
LiteLLM 支持智谱 AI，模型名称：`zhipu/glm-4`

### 3. 系统提示注入

#### 3.1 系统提示设计
**文件**: `agent/context.py` (已有 ContextBuilder)

```python
SYSTEM_PROMPT = """你是 SocratX，一个智能 AI 助手。
- 你友好、专业
- 你使用简洁的中文回复
- 首次问候时回复"你好，我是 SocratX"
"""
```

### 4. 模块依赖

```
main.py (FastAPI 入口)
  └── utils/logger.py (新建)
  └── config/loader.py (加载配置)
  └── providers/litellm_provider.py (已有，需配置 GLM-4)
  └── agent/context.py (已有，注入系统提示)
```

---

## 实现步骤

1. **创建 logger 单例** (`utils/logger.py`)
2. **配置日志文件** (3 个 logger)
3. **更新配置** (GLM-4.7 配置)
4. **更新 main.py** (使用新 logger)
5. **更新 litellm_provider.py** (记录 AI 日志)
6. **更新 context.py** (系统提示)
7. **测试对话流程**

---

## 风险与注意

1. **API Key**: 需要用户提供智谱 AI API Key
2. **模型名称**: 确认 GLM-4.7 在 LiteLLM 中的正确名称
3. **日志轮转**: 是否需要日志轮转（避免文件过大）

---

## 待确认

1. 智谱 AI API Key 是否已配置？
2. 日志文件存放位置：`services/agent/logs/` 可以吗？
3. 是否需要日志轮转功能？
