from fastapi import HTTPException, status as http_status

from app.ai.orchestrator import AIOrchestrator
from app.ai.providers.base import AIGenerationError
from app.ai.mock_content_generator import generate_mock_lesson_content
from app.core.config import settings
from app.repositories.ai_request_log_repository import AIRequestLogRepository

from sqlalchemy.orm import Session

from app.ai.mock_content_generator import generate_mock_lesson_content
from app.models.enums import LessonStatus
from app.models.user import User
from app.repositories.lesson_plan_repository import LessonPlanRepository
from app.schemas.lesson_plan import LessonPlanGenerateRequest, LessonPlanGenerateResponse


class LessonPlanService:
    def __init__(self, db: Session):
        self.db = db
        self.lesson_plans = LessonPlanRepository(db)
        self.ai_logs = AIOrchestrator()
        self.orchestrator = AIOrchestrator()

    def generate(self, *, request, teacher):
        lesson_plan = self.lesson_plans.create(
            school_id=teacher.school_id, teacher_id=teacher.id,
            grade=request.grade, subject=request.subject, topic=request.topic,
            student_count=request.student_count, duration_minutes=request.duration_minutes,
            curriculum=request.curriculum, ability_level=request.ability_level,
            learning_context=request.learning_context, additional_instructions=request.additional_instructions,
            status=LessonStatus.DRAFT,
        )

        if settings.use_mock_ai:
            content_fields = generate_mock_lesson_content(request)
            is_mock, provider_name, model_name = True, None, None
        else:
            try:
                result, usage, provider_name, prompt_version = self.orchestrator.generate_lesson_content(request)
            except AIGenerationError as exc:
                self.ai_logs.log(
                    school_id=teacher.school_id, user_id=teacher.id, purpose="lesson_generation",
                    provider=settings.ai_provider, model=settings.anthropic_model, prompt_tokens=0,
                    completion_tokens=0, latency_ms=0, status="error", error_message=str(exc),
                )
                self.db.commit()
                raise HTTPException(
                    status_code=http_status.HTTP_502_BAD_GATEWAY,
                    detail="Lesson generation failed. Please try again.",
                )
            content_fields = result.model_dump()
            is_mock = False
            model_name = settings.anthropic_model if provider_name == "anthropic" else settings.openai_model
            self.ai_logs.log(
                school_id=teacher.school_id, user_id=teacher.id, purpose="lesson_generation",
                provider=provider_name, model=model_name, prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"], latency_ms=usage["latency_ms"], status="success",
            )

        content = self.lesson_plans.attach_content(lesson_plan=lesson_plan, content_fields=content_fields, is_mock=is_mock)
        content.ai_provider_used = provider_name
        content.ai_model_used = model_name
        lesson_plan.status = LessonStatus.GENERATED
        lesson_plan.generated_at = content.generated_at
        self.db.commit()
        self.db.refresh(lesson_plan)
        self.db.refresh(content)

        return LessonPlanGenerateResponse(
            lesson_plan_id=lesson_plan.id, status=lesson_plan.status.value, is_mock=content.is_mock,
            grade=lesson_plan.grade, subject=lesson_plan.subject, topic=lesson_plan.topic,
            student_count=lesson_plan.student_count, duration_minutes=lesson_plan.duration_minutes,
            learning_objectives=content.learning_objectives, teaching_activities=content.teaching_activities,
            differentiated_activities=content.differentiated_activities, assessment_questions=content.assessment_questions,
            marking_rubric=content.marking_rubric, homework=content.homework, revision_questions=content.revision_questions,
            generated_at=content.generated_at,
        )