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
from typing import List, Optional, Any
import logging
import json

# 导入内部模块
from agent.loop import AgentLoop, AgentConfig, create_agent_loop
from agent.session import SessionManager
from agent.memory import MemoryStore
from agent.tools.registry import create_default_registry
from providers.litellm_provider import create_provider
from config.loader import init_config
from config.schema import SocratXConfig
from bus.events import InboundMessage, OutboundMessage, MessageType
from bus.queue import get_message_bus

# 导入统一日志系统
from utils.logger import logger

# 配置 AI 日志 handler
def _setup_ai_logger():
    """配置 AI 日志记录器"""
    ai_logger = logging.getLogger("socratx.ai")
    ai_logger.setLevel(logging.DEBUG)
    ai_logger.propagate = False
    
    # 清除现有 handler
    ai_logger.handlers.clear()
    
    # 日志文件
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # AI 日志 handler
    ai_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ai_handler = logging.FileHandler(log_dir / "ai.log", encoding="utf-8")
    ai_handler.setFormatter(ai_format)
    ai_logger.addHandler(ai_handler)

_setup_ai_logger()


# ===== 请求/响应模型 =====


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default="default", description="会话 ID")
    user_id: str = Field(default="default", description="用户 ID")
    model: Optional[str] = Field(default=None, description="覆盖默认模型")
    stream: bool = Field(default=False, description="是否使用流式输出")


class ToolCall(BaseModel):
    """工具调用信息"""
    id: str
    name: str
    arguments: dict


class ChatResponse(BaseModel):
    """对话响应"""
    content: str = Field(..., description="AI 回复内容")
    session_id: str = Field(..., description="会话 ID")
    model: str = Field(..., description="使用的模型")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="使用的工具")
    usage: Optional[dict] = Field(default=None, description="Token 使用情况")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[dict]
    total: int


class MemoryRequest(BaseModel):
    """记忆更新请求"""
    content: str = Field(..., description="记忆内容")
    section: Optional[str] = Field(default=None, description="目标章节")


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    updates: dict = Field(..., description="配置更新")


class ConfigResponse(BaseModel):
    """配置响应"""
    config: dict


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    components: dict


# ===== 全局状态 =====

# 全局组件
_agent_loop: Optional[AgentLoop] = None
_session_manager: Optional[SessionManager] = None
_memory_store: Optional[MemoryStore] = None
_config: Optional[SocratXConfig] = None


def _parse_tool_arguments(arguments: Any) -> dict:
    """
    解析工具调用参数

    arguments 应该已经是 dict（由 litellm_provider._parse_response 处理）
    但为了保险，做类型检查
    """
    if isinstance(arguments, dict):
        return arguments
    # 如果不是 dict，尝试用 json_repair 解析
    if isinstance(arguments, str):
        try:
            import json_repair
            return json_repair.loads(arguments)
        except:
            pass
    return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global _agent_loop, _session_manager, _memory_store, _config

    logger.system("Starting SocratX Agent API...")

    # 初始化配置
    _config = init_config()
    logger.system(f"Config loaded: {_config.agent.model}")

    # 初始化组件
    _session_manager = SessionManager()
    _memory_store = MemoryStore(_config.agent.workspace)

    # 创建工具注册表
    tool_registry = await create_default_registry()
    logger.system(f"Tool registry initialized with {len(tool_registry.list_tools())} tools")

    # 创建 LLM 提供商
    # 从配置中获取提供商 - 使用关键词匹配（参考 nanobot）
    model_name = _config.agent.model
    model_lower = model_name.lower()
    
    # 从 providers registry 获取关键词匹配
    from providers.registry import PROVIDERS
    
    provider_config = None
    provider_name = None
    
    for spec in PROVIDERS:
        p = getattr(_config.providers, spec.name, None)
        if p and p.api_key and any(kw in model_lower for kw in spec.keywords):
            provider_config = p
            provider_name = spec.name
            break
    
    # 如果没有匹配，尝试从模型前缀获取
    if not provider_config:
        prefix = model_name.split("/")[0] if "/" in model_name else "openai"
        if hasattr(_config.providers, prefix):
            provider_config = getattr(_config.providers, prefix)
            provider_name = prefix
    
    api_key = provider_config.api_key if provider_config else None
    api_base = provider_config.api_base if provider_config else None
    
    logger.system(f"Creating LLM provider: {provider_name or 'unknown'} for model {model_name}")
    logger.system(f"API Key: {'***' if api_key else 'None'}")
    logger.system(f"API Base: {api_base if api_base else 'None'}")
    
    llm_provider = await create_provider(
        model=model_name,
        api_key=api_key,
        api_base=api_base,
    )

    # 创建 AgentLoop
    from agent.loop import AgentLoop
    _agent_loop = AgentLoop(
        config=AgentConfig(
            model=_config.agent.model,
            temperature=_config.agent.temperature,
            max_tokens=_config.agent.max_tokens,
            max_iterations=_config.agent.max_iterations,
            workspace=_config.agent.workspace,
            memory_enabled=_config.agent.memory_enabled,
        ),
        session_manager=_session_manager,
        memory_store=_memory_store,
        tool_registry=tool_registry,
    )
    _agent_loop.set_llm_provider(llm_provider)

    # 启动消息总线
    message_bus = get_message_bus()
    await message_bus.start()
    logger.system("Message bus started")

    logger.system("SocratX Agent API started successfully")

    yield

    # 清理
    logger.system("Shutting down SocratX Agent API...")
    await message_bus.stop()
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
    message_bus = get_message_bus()
    bus_stats = message_bus.get_stats()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        components={
            "agent_loop": _agent_loop is not None,
            "session_manager": _session_manager is not None,
            "memory_store": _memory_store is not None,
            "message_bus": bus_stats,
        },
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    处理对话请求

    这是主要的 API 端点，处理用户消息并返回 AI 响应
    """
    if _agent_loop is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        # 记录用户输入
        logger.conversation(
            session_id=request.session_id,
            role="USER",
            content=request.message,
        )

        # 使用 AgentLoop 处理消息
        response = await _agent_loop.run(
            message=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
        )

        # 记录 AI 响应
        logger.conversation(
            session_id=request.session_id,
            role="AI",
            content=response.content,
        )

        return ChatResponse(
            content=response.content or "",
            session_id=request.session_id,
            model=_config.agent.model if _config else "unknown",
            tool_calls=[
                ToolCall(
                    id=tc.get("id", ""),
                    name=tc.get("name", ""),
                    arguments=tc.get("arguments", {}),
                )
                for tc in (response.tool_calls or [])
            ],
            usage=response.metadata.get("usage"),
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get("/api/sessions", response_model=SessionListResponse, tags=["Sessions"])
async def list_sessions(
    user_id: Optional[str] = None,
    limit: int = 100,
):
    """获取会话列表"""
    if _session_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session manager not initialized",
        )

    sessions = _session_manager.list_sessions(user_id=user_id, limit=limit)

    return SessionListResponse(
        sessions=[s.to_dict() for s in sessions],
        total=len(sessions),
    )


@app.get("/api/sessions/{session_id}", tags=["Sessions"])
async def get_session(session_id: str):
    """获取会话详情"""
    if _session_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session manager not initialized",
        )

    session = _session_manager.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    return session.to_dict()


@app.delete("/api/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """删除会话"""
    if _session_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session manager not initialized",
        )

    success = _session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {session_id}",
        )

    return {"deleted": True, "session_id": session_id}


@app.get("/api/memory", tags=["Memory"])
async def get_memory():
    """获取长期记忆"""
    if _memory_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory store not initialized",
        )

    content = await _memory_store.get_memory()
    return {"content": content}


@app.post("/api/memory", tags=["Memory"])
async def update_memory(request: MemoryRequest):
    """更新长期记忆"""
    if _memory_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory store not initialized",
        )

    await _memory_store.update_memory(request.content, request.section)
    return {"updated": True}


@app.get("/api/memory/search", tags=["Memory"])
async def search_memory(query: str, limit: int = 10):
    """搜索记忆"""
    if _memory_store is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory store not initialized",
        )

    results = await _memory_store.search_history(query, limit)
    return {"results": results}


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
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    from config.loader import update_config as uc

    updated = uc(request.updates)
    return {"updated": True, "config": updated.model_dump()}


@app.get("/api/tools", tags=["Tools"])
async def list_tools():
    """列出可用工具"""
    if _agent_loop is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    tools = _agent_loop.tool_registry.get_tool_schemas()
    return {"tools": tools, "count": len(tools)}


@app.get("/api/stats", tags=["System"])
async def get_stats():
    """获取系统统计信息"""
    stats = {}

    if _session_manager:
        stats["sessions"] = _session_manager.get_stats()

    if _memory_store:
        stats["memory"] = _memory_store.get_stats()

    message_bus = get_message_bus()
    stats["message_bus"] = message_bus.get_stats()

    return stats


if __name__ == "__main__":
    import uvicorn

    # 从环境变量或配置读取端口
    port = 8000

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
    )
