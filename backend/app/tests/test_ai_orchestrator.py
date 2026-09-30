from unittest.mock import MagicMock, patch

import pytest

from app.ai.orchestrator import AIOrchestrator
from app.ai.providers.base import AIGenerationError
from app.schemas.lesson_plan import LessonContentAIResult, TeachingActivity, DifferentiatedActivity, AssessmentQuestion, RubricCriterion, RubricPerformanceLevel


def _fake_result():
    return LessonContentAIResult(
        learning_objectives=["Objective one."],
        teaching_activities=[
            TeachingActivity(
                title="Intro",
                teacher_actions="Introduces the topic.",
                student_actions="Listen and take notes.",
                duration_minutes=10,
            )
        ],
        differentiated_activities=[DifferentiatedActivity(target_group="below_grade_level", description="desc")],
        assessment_questions=[AssessmentQuestion(question_text="Q?", question_type="short_answer", max_score=5)],
        marking_rubric=[
            RubricCriterion(
                criterion="Understanding",
                description="desc",
                max_points=5,
                performance_levels=[
                    RubricPerformanceLevel(level="Proficient", descriptor="Clear and accurate.", points=5),
                    RubricPerformanceLevel(level="Developing", descriptor="Partially correct.", points=2),
                ],
            )
        ],
        homework=["Homework item."],
        revision_questions=["Revision Q?"],
    )


class FakeRequest:
    grade = "Grade 10"
    subject = "English"
    topic = "Poetry"
    student_count = 40
    duration_minutes = 60
    ability_level = "mixed"
    curriculum = None
    learning_context = None
    additional_instructions = None


def test_orchestrator_returns_parsed_result_on_success():
    fake_provider = MagicMock()
    fake_provider.name = "anthropic"
    fake_provider.generate_structured.return_value = (
        _fake_result(),
        {"prompt_tokens": 100, "completion_tokens": 200, "latency_ms": 50},
    )

    with patch("app.ai.orchestrator.get_provider", return_value=fake_provider):
        orchestrator = AIOrchestrator()
        result, usage, provider_name, prompt_version = orchestrator.generate_lesson_content(FakeRequest())

    assert provider_name == "anthropic"
    assert usage["prompt_tokens"] == 100
    assert len(result.learning_objectives) == 1
    fake_provider.generate_structured.assert_called_once()


def test_orchestrator_retries_then_succeeds():
    fake_provider = MagicMock()
    fake_provider.name = "anthropic"
    fake_provider.generate_structured.side_effect = [
        AIGenerationError("bad output"),
        (_fake_result(), {"prompt_tokens": 10, "completion_tokens": 20, "latency_ms": 5}),
    ]

    with patch("app.ai.orchestrator.get_provider", return_value=fake_provider):
        orchestrator = AIOrchestrator()
        result, usage, provider_name, _ = orchestrator.generate_lesson_content(FakeRequest())

    assert fake_provider.generate_structured.call_count == 2
    assert len(result.learning_objectives) == 1


def test_orchestrator_raises_after_exhausting_retries():
    fake_provider = MagicMock()
    fake_provider.name = "anthropic"
    fake_provider.generate_structured.side_effect = AIGenerationError("always fails")

    with patch("app.ai.orchestrator.get_provider", return_value=fake_provider):
        orchestrator = AIOrchestrator()
        with pytest.raises(AIGenerationError):
            orchestrator.generate_lesson_content(FakeRequest())

    # ai_max_retries default is 2, so 3 total attempts
    assert fake_provider.generate_structured.call_count == 3