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

    def generate(self, *, request: LessonPlanGenerateRequest, teacher: User) -> LessonPlanGenerateResponse:
        lesson_plan = self.lesson_plans.create(
            school_id=teacher.school_id,
            teacher_id=teacher.id,
            grade=request.grade,
            subject=request.subject,
            topic=request.topic,
            student_count=request.student_count,
            duration_minutes=request.duration_minutes,
            curriculum=request.curriculum,
            ability_level=request.ability_level,
            learning_context=request.learning_context,
            additional_instructions=request.additional_instructions,
            status=LessonStatus.DRAFT,
        )

        # This is the ONLY line that changes in Stage 5:
        # content_fields = ai_orchestrator.generate_lesson_content(request, teacher.school_id)
        content_fields = generate_mock_lesson_content(request)

        content = self.lesson_plans.attach_content(
            lesson_plan=lesson_plan, content_fields=content_fields, is_mock=True
        )

        lesson_plan.status = LessonStatus.GENERATED
        lesson_plan.generated_at = content.generated_at
        self.db.commit()
        self.db.refresh(lesson_plan)
        self.db.refresh(content)

        return LessonPlanGenerateResponse(
            lesson_plan_id=lesson_plan.id,
            status=lesson_plan.status.value,
            is_mock=content.is_mock,
            grade=lesson_plan.grade,
            subject=lesson_plan.subject,
            topic=lesson_plan.topic,
            student_count=lesson_plan.student_count,
            duration_minutes=lesson_plan.duration_minutes,
            learning_objectives=content.learning_objectives,
            teaching_activities=content.teaching_activities,
            differentiated_activities=content.differentiated_activities,
            assessment_questions=content.assessment_questions,
            marking_rubric=content.marking_rubric,
            homework=content.homework,
            revision_questions=content.revision_questions,
            generated_at=content.generated_at,
        )