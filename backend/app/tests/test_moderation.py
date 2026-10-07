from unittest.mock import MagicMock, patch

import pytest

from app.ai.moderation import ModerationFlaggedError, assert_not_flagged
from app.core.config import settings


def _fake_openai_client(*, flagged: bool, categories: dict | None = None):
    """Build a stand-in for OpenAI(...) whose moderations.create() returns a canned result."""
    result = MagicMock()
    result.flagged = flagged
    result.categories.model_dump.return_value = categories or {}
    client = MagicMock()
    client.moderations.create.return_value.results = [result]
    return client


@pytest.fixture
def moderation_on(monkeypatch):
    monkeypatch.setattr(settings, "moderation_enabled", True)
    monkeypatch.setattr(settings, "openai_api_key", "test-key")


def test_assert_not_flagged_raises_on_flagged_content(moderation_on):
    client = _fake_openai_client(flagged=True, categories={"violence": True, "hate": False})
    with patch("app.ai.moderation.OpenAI", return_value=client):
        with pytest.raises(ModerationFlaggedError) as exc_info:
            assert_not_flagged("some harmful text")
    assert "violence" in str(exc_info.value)
    assert "hate" not in str(exc_info.value)


def test_assert_not_flagged_passes_clean_content(moderation_on):
    client = _fake_openai_client(flagged=False)
    with patch("app.ai.moderation.OpenAI", return_value=client):
        assert_not_flagged("a normal photosynthesis answer")  # must not raise


def test_assert_not_flagged_fails_open_when_service_errors(moderation_on):
    client = MagicMock()
    client.moderations.create.side_effect = RuntimeError("service down")
    with patch("app.ai.moderation.OpenAI", return_value=client):
        assert_not_flagged("anything")  # must not raise