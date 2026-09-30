from app.ai.prompts.submission_analysis_v1 import (
    PROMPT_VERSION as ANALYSIS_PROMPT_VERSION,
    SYSTEM_PROMPT as ANALYSIS_SYSTEM_PROMPT,
    build_user_prompt as build_analysis_user_prompt,
)
from app.ai.prompts.reteach_recommendation_v1 import (
    PROMPT_VERSION as RETEACH_PROMPT_VERSION,
    SYSTEM_PROMPT as RETEACH_SYSTEM_PROMPT,
    build_user_prompt as build_reteach_user_prompt,
)
from app.schemas.reteach import ReteachRecommendationAIResult
from app.schemas.submission_analysis import SubmissionAnalysisAIResult
from app.ai.provider_registry import get_provider
from app.ai.providers.base import AIGenerationError
from app.core.config import settings
from app.schemas.lesson_plan import LessonContentAIResult
from app.ai.prompts.lesson_generation_v2 import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt


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
    def analyze_submission(self, questions_with_answers: list[dict], *, provider_name: str | None = None):
        provider = get_provider(provider_name)
        user_prompt = build_analysis_user_prompt(questions_with_answers)

        last_error = None
        for _ in range(settings.ai_max_retries + 1):
            try:
                parsed, usage = provider.generate_structured(
                    system_prompt=ANALYSIS_SYSTEM_PROMPT, user_prompt=user_prompt, schema=SubmissionAnalysisAIResult
                )
                return parsed, usage, provider.name, ANALYSIS_PROMPT_VERSION
            except AIGenerationError as exc:
                last_error = exc
        raise last_error
    
    def generate_reteach_recommendations(self, concepts: list[dict], *, provider_name: str | None = None):
        provider = get_provider(provider_name)
        user_prompt = build_reteach_user_prompt(concepts)

        last_error = None
        for _ in range(settings.ai_max_retries + 1):
            try:
                parsed, usage = provider.generate_structured(
                    system_prompt=RETEACH_SYSTEM_PROMPT, user_prompt=user_prompt, schema=ReteachRecommendationAIResult
                )
                return parsed, usage, provider.name, RETEACH_PROMPT_VERSION
            except AIGenerationError as exc:
                last_error = exc
        raise last_error