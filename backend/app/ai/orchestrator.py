from app.ai.prompts.lesson_generation_v1 import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt
from app.ai.provider_registry import get_provider
from app.ai.providers.base import AIGenerationError
from app.core.config import settings
from app.schemas.lesson_plan import LessonContentAIResult


class AIOrchestrator:
    def generate_lesson_content(self, request, *, provider_name: str | None = None):
        provider = get_provider(provider_name)
        user_prompt = build_user_prompt(request)

        last_error = None
        for _ in range(settings.ai_max_retries + 1):
            try:
                parsed, usage = provider.generate_structured(
                    system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt, schema=LessonContentAIResult
                )
                return parsed, usage, provider.name, PROMPT_VERSION
            except AIGenerationError as exc:
                last_error = exc
        raise last_error