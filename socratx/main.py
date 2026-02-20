"""
SocratX Agent API - FastAPI 主入口

提供 HTTP API 接口供 Tauri 前端调用
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio

# 导入内部模块
from providers.litellm_provider import LiteLLMProvider
from config.loader import load_config
from config.schema import Config
from agent.tools.registry import ToolRegistry
from agent.context import ContextBuilder

# 导入统一日志系统
from utils.logger import logger


# ===== 请求/响应模型 =====


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default="default", description="会话 ID")
    user_id: str = Field(default="default", description="用户 ID")


class ChatResponse(BaseModel):
    """对话响应"""
    content: str = Field(..., description="AI 回复内容")
    session_id: str = Field(..., description="会话 ID")
    model: str = Field(..., description="使用的模型")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[dict]
    total: int


class MemoryRequest(BaseModel):
    """记忆更新请求"""
    content: str = Field(..., description="记忆内容")
    section: Optional[str] = Field(default=None, description="目标章节")


class ConfigResponse(BaseModel):
    """配置响应"""
    config: dict


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str


# ===== 全局状态 =====

_config: Optional[Config] = None
_tool_registry: Optional[ToolRegistry] = None
_llm_provider: Optional[LiteLLMProvider] = None
_context_builder: Optional[ContextBuilder] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global _config, _tool_registry, _llm_provider, _context_builder

    logger.system("Starting SocratX Agent API...")

    # 初始化配置
    _config = load_config()
    logger.system(f"Config loaded: {_config.agents.defaults.model}")

    # 初始化 ContextBuilder（包含系统提示词、技能、记忆）
    _context_builder = ContextBuilder(_config.workspace_path)
    logger.system(f"Context builder initialized with workspace: {_config.workspace_path}")

    # 创建工具注册表
    _tool_registry = ToolRegistry()
    
    # 注册文件工具
    from agent.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
    _tool_registry.register(ReadFileTool())
    _tool_registry.register(WriteFileTool())
    _tool_registry.register(ListDirTool())
    
    # 注册 Shell 工具
    from agent.tools.shell import ExecTool
    _tool_registry.register(ExecTool())
    
    # 注册 Web 工具
    from agent.tools.web import WebSearchTool, WebFetchTool
    _tool_registry.register(WebSearchTool())
    _tool_registry.register(WebFetchTool())
    
    logger.system(f"Tool registry initialized with {len(_tool_registry.tool_names)} tools")

    # 创建 LLM 提供商
    model_name = _config.agents.defaults.model
    provider_name = _config.get_provider_name(model_name)
    p = _config.get_provider(model_name)
    
    api_key = p.api_key if p else None
    api_base = _config.get_api_base(model_name) if p else None

    logger.system(f"Creating LLM provider: {provider_name or 'unknown'} for model {model_name}")

    _llm_provider = LiteLLMProvider(
        api_key=api_key,
        api_base=api_base,
        default_model=model_name,
        provider_name=provider_name,
    )

    logger.system("SocratX Agent API started successfully")

    yield

    # 清理
    logger.system("Shutting down SocratX Agent API...")
    logger.system("SocratX Agent API stopped")


# ===== FastAPI 应用 =====

app = FastAPI(
    title="SocratX Agent API",
    description="SocratX AI 助手后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== API 端点 =====


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "name": "SocratX Agent API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    处理对话请求 - 使用完整的上下文构建（系统提示词 + 技能 + 记忆）
    """
    if _llm_provider is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM provider not initialized",
        )

    try:
        # 记录用户输入
        logger.conversation(
            session_id=request.session_id,
            role="USER",
            content=request.message,
        )

        # 构建系统提示词（包含身份、技能、记忆）
        system_prompt = _context_builder.build_system_prompt()

        # 调用 LLM（带系统提示词和工具）
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.message}
        ]

        # 记录 AI 请求到 ai.log（包含完整提示词）
        logger.ai_request(_config.agents.defaults.model, messages)

        # 获取工具定义
        tools = _tool_registry.get_definitions()

        # 调用 LLM（带工具）
        response = await _llm_provider.chat(messages, tools=tools)

        # 处理工具调用（如果有）
        max_iterations = 5
        iteration = 0
        conversation_history = messages.copy()

        while response.tool_calls and iteration < max_iterations:
            iteration += 1
            logger.system(f"Processing {len(response.tool_calls)} tool calls (iteration {iteration})")

            # 执行所有工具调用
            tool_results = []
            for tool_call in response.tool_calls:
                logger.system(f"Executing tool: {tool_call.name}")
                tool_result = await _tool_registry.execute(tool_call.name, tool_call.arguments)
                logger.system(f"Tool result: {tool_result[:200]}...")
                tool_results.append(f"[{tool_call.name}]: {tool_result}")

            # 添加工具调用结果到对话历史（使用 user 角色，因为 GLM 不支持 tool 角色）
            conversation_history.append({
                "role": "user",
                "content": "Tool execution results:\n" + "\n".join(tool_results)
            })

            # 再次调用 LLM 获取最终响应
            response = await _llm_provider.chat(conversation_history, tools=tools)

        # 记录 AI 响应
        logger.conversation(
            session_id=request.session_id,
            role="AI",
            content=response.content,
        )

        return ChatResponse(
            content=response.content or "",
            session_id=request.session_id,
            model=_config.agents.defaults.model if _config else "unknown",
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get("/api/sessions", tags=["Sessions"])
async def list_sessions(
    user_id: Optional[str] = None,
    limit: int = 100,
):
    """获取会话列表"""
    # TODO: 实现会话管理
    return SessionListResponse(sessions=[], total=0)


@app.get("/api/sessions/{session_id}", tags=["Sessions"])
async def get_session(session_id: str):
    """获取会话详情"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session management not implemented",
    )


@app.delete("/api/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """删除会话"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session management not implemented",
    )


@app.get("/api/memory", tags=["Memory"])
async def get_memory():
    """获取长期记忆"""
    if _config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Config not initialized",
        )

    # 从 workspace 读取 MEMORY.md
    memory_file = _config.workspace_path / "memory" / "MEMORY.md"
    content = ""
    if memory_file.exists():
        content = memory_file.read_text(encoding='utf-8')
    
    return {"content": content}


@app.post("/api/memory", tags=["Memory"])
async def update_memory(request: MemoryRequest):
    """更新长期记忆"""
    if _config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Config not initialized",
        )

    # 写入 workspace 的 MEMORY.md
    memory_dir = _config.workspace_path / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file = memory_dir / "MEMORY.md"
    
    # 追加内容
    with open(memory_file, "a", encoding='utf-8') as f:
        f.write(f"\n\n## {request.section or 'General'}\n{request.content}\n")
    
    return {"updated": True}


@app.get("/api/config", response_model=ConfigResponse, tags=["Config"])
async def get_config():
    """获取当前配置"""
    if _config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Config not initialized",
        )

    return ConfigResponse(config=_config.model_dump())


@app.post("/api/config", tags=["Config"])
async def update_config(request: dict):
    """更新配置"""
    from config.loader import save_config
    
    if _config is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Config not initialized",
        )

    # 简单更新（实际应该更深层次合并）
    updates = request.get("updates", {})
    if "model" in updates:
        _config.agents.defaults.model = updates["model"]
    
    save_config(_config)
    return {"updated": True, "config": _config.model_dump()}


@app.get("/api/tools", tags=["Tools"])
async def list_tools():
    """列出可用工具"""
    if _tool_registry is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tool registry not initialized",
        )

    tools = _tool_registry.get_definitions()
    return {"tools": tools, "count": len(tools)}


if __name__ == "__main__":
    import uvicorn

    port = 8000

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
    )
