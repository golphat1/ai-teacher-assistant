import logging

from openai import OpenAI

from app.ai.providers.base import AIGenerationError
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModerationFlaggedError(AIGenerationError):
    """Raised when AI-generated content is flagged by the moderation check.
    Subclasses AIGenerationError so it's caught by the retry/error-handling
    code every AI call site already has — no new exception handling needed."""


def assert_not_flagged(text: str) -> None:
    if not settings.moderation_enabled or not text.strip():
        return

    if not settings.openai_api_key:
        # Fail OPEN, not closed: a school running Anthropic-only with no OpenAI key
        # configured must not have every generation silently blocked by a check
        # it never opted into providing credentials for. Logged so this is
        # visible to an operator, not silently invisible.
        logger.warning("Moderation check skipped: no OPENAI_API_KEY configured.")
        return

    client = OpenAI(api_key=settings.openai_api_key)
    try:
        response = client.moderations.create(input=text)
    except Exception as exc:
        # The moderation service itself being down must not block core app
        # functionality — fail open here too, but log loudly.
        logger.warning("Moderation check failed to run: %s", exc)
        return

    result = response.results[0]
    if result.flagged:
        categories = [name for name, value in result.categories.model_dump().items() if value]
        raise ModerationFlaggedError(
            f"Generated content was flagged by moderation: {', '.join(categories) or 'unspecified category'}"
        )