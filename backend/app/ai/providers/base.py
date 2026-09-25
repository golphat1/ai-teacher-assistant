from typing import Protocol, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIGenerationError(Exception):
    """Raised when a provider fails to return valid structured output."""


class AIProvider(Protocol):
    name: str

    def generate_structured(
        self, *, system_prompt: str, user_prompt: str, schema: Type[T], max_tokens: int = 4096
    ) -> tuple[T, dict]:
        """Returns (parsed_object, usage_metadata)."""
        ...