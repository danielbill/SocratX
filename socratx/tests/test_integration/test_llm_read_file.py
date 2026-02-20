"""Integration test - LLM reads file content"""
import pytest
from pathlib import Path

from config.loader import load_config
from providers.litellm_provider import LiteLLMProvider
from agent.tools.registry import ToolRegistry
from agent.tools.filesystem import ReadFileTool


@pytest.mark.asyncio
async def test_llm_read_file():
    """Test LLM calling read_file tool - read D:/hello.txt"""
    config = load_config()
    
    provider = LiteLLMProvider(
        api_key=config.get_api_key(),
        api_base=config.get_api_base(),
        default_model=config.agents.defaults.model,
        provider_name=config.get_provider_name(),
    )
    
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    
    tools = registry.get_definitions()
    test_file = "D:/hello.txt"
    
    messages = [
        {
            "role": "user", 
            "content": f"Please read the file at {test_file} and tell me its content. Call read_file tool with path parameter."
        }
    ]
    
    print(f"\nModel: {config.agents.defaults.model}")
    print(f"Test file: {test_file}")
    
    response = await provider.chat(messages, tools=tools)
    
    print(f"LLM response: {response.content}")
    print(f"Tool calls: {len(response.tool_calls)}")
    
    for tool_call in response.tool_calls:
        print(f"Execute: {tool_call.name}")
        print(f"Args: {tool_call.arguments}")
        result = await registry.execute(tool_call.name, tool_call.arguments)
        print(f"Result: {result}")
    
    assert Path(test_file).exists(), f"File {test_file} not found"
    
    content = Path(test_file).read_text(encoding='utf-8')
    print(f"[OK] File content: {content}")
