from app.ai.providers.anthropic_adapter import AnthropicAdapter
from app.ai.providers.openai_adapter import OpenAIAdapter
from app.core.config import settings

_instances = {}


def get_provider(name: str | None = None):
    name = name or settings.ai_provider
    if name not in _instances:
        if name == "anthropic":
            _instances[name] = AnthropicAdapter()
        elif name == "openai":
            _instances[name] = OpenAIAdapter()
        else:
            raise ValueError(f"Unknown AI provider: {name}")
    return _instances[name]