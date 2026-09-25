import time
from openai import OpenAI, APIError
from pydantic import ValidationError

from app.ai.providers.base import AIGenerationError
from app.core.config import settings


class OpenAIAdapter:
    name = "openai"

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate_structured(self, *, system_prompt, user_prompt, schema, max_tokens=4096):
        start = time.monotonic()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema(), "strict": True},
                },
            )
        except APIError as exc:
            raise AIGenerationError(f"OpenAI API error: {exc}") from exc

        latency_ms = int((time.monotonic() - start) * 1000)
        try:
            parsed = schema.model_validate_json(response.choices[0].message.content)
        except ValidationError as exc:
            raise AIGenerationError(f"AI output failed schema validation: {exc}") from exc

        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "latency_ms": latency_ms,
        }
        return parsed, usage