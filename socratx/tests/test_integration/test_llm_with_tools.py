"""Integration test - real LLM call with tool calling"""
import pytest
from pathlib import Path

from config.loader import load_config
from providers.litellm_provider import LiteLLMProvider
from agent.tools.registry import ToolRegistry
from agent.tools.filesystem import WriteFileTool


@pytest.mark.asyncio
async def test_llm_with_file_tool_write_file():
    """Test LLM calling file write tool - create hello.txt in D: root"""
    config = load_config()
    
    provider = LiteLLMProvider(
        api_key=config.get_api_key(),
        api_base=config.get_api_base(),
        default_model=config.agents.defaults.model,
        provider_name=config.get_provider_name(),
    )
    
    registry = ToolRegistry()
    registry.register(WriteFileTool())
    
    tools = registry.get_definitions()
    test_file = "D:/hello.txt"
    
    messages = [
        {
            "role": "user", 
            "content": f"Please create a file at {test_file} with content 'hello'. Call write_file tool with path and content parameters."
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
    
    assert Path(test_file).exists(), f"File {test_file} not created"
    
    content = Path(test_file).read_text(encoding='utf-8')
    assert "hello" in content.lower(), f"File content does not contain 'hello': {content}"
    
    print(f"[OK] Test passed! File created: {test_file}")
    print(f"Content: {content}")
