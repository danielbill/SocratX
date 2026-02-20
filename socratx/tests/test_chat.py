"""Test chat completion"""
import pytest
from config.loader import load_config
from providers.litellm_provider import LiteLLMProvider


@pytest.mark.asyncio
async def test_chat_completion():
    """Test basic chat completion"""
    config = load_config()

    provider_name = config.get_provider_name()
    api_key = config.get_api_key()
    api_base = config.get_api_base()
    model = config.agents.defaults.model

    print(f"\nModel: {model}")
    print(f"Provider: {provider_name}")

    provider = LiteLLMProvider(
        api_key=api_key,
        api_base=api_base,
        default_model=model,
        provider_name=provider_name,
    )

    response = await provider.chat([
        {'role': 'user', 'content': 'Hello, introduce yourself in one sentence'}
    ])

    assert response.content is not None
    assert len(response.content) > 0
    print(f"\nResponse: {response.content}")
