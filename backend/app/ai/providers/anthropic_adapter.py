import time
import anthropic
from pydantic import ValidationError

from app.ai.providers.base import AIGenerationError
from app.core.config import settings


class AnthropicAdapter:
    name = "anthropic"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate_structured(self, *, system_prompt, user_prompt, schema, max_tokens=4096):
        tool = {
            "name": "emit_result",
            "description": "Return the result matching the required schema.",
            "input_schema": schema.model_json_schema(),
        }
        start = time.monotonic()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                tools=[tool],
                tool_choice={"type": "tool", "name": "emit_result"},
            )
        except anthropic.APIError as exc:
            raise AIGenerationError(f"Anthropic API error: {exc}") from exc

        latency_ms = int((time.monotonic() - start) * 1000)
        block = next((b for b in response.content if b.type == "tool_use"), None)
        if block is None:
            raise AIGenerationError("No tool_use block in Anthropic response.")

        try:
            parsed = schema.model_validate(block.input)
        except ValidationError as exc:
            raise AIGenerationError(f"AI output failed schema validation: {exc}") from exc

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "latency_ms": latency_ms,
        }
        return parsed, usage