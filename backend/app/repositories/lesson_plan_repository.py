import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.lesson_content import LessonContent
from app.models.lesson_plan import LessonPlan


class LessonPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, school_id: uuid.UUID, teacher_id: uuid.UUID, **fields) -> LessonPlan:
        lesson_plan = LessonPlan(school_id=school_id, teacher_id=teacher_id, **fields)
        self.db.add(lesson_plan)
        self.db.flush()
        return lesson_plan

    def attach_content(self, *, lesson_plan: LessonPlan, content_fields: dict, is_mock: bool) -> LessonContent:
        content = LessonContent(
            lesson_plan_id=lesson_plan.id,
            learning_objective=content_fields["learning_objectives"],
            teaching_activity=content_fields["teaching_activities"],
            differentiated_activities=content_fields["differentiated_activities"],
            assessment_questions=content_fields["assessment_questions"],
            marking_rubric=content_fields["marking_rubric"],
            homework=content_fields.get("homework"),
            revision_questions=content_fields["revision_questions"],
            is_mock=is_mock,
            ai_provider_used="mock",
            ai_model_used="mock",
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(content)
        self.db.flush()
        return content

    def get_by_id(self, lesson_plan_id: uuid.UUID, *, school_id: uuid.UUID) -> LessonPlan | None:
        return (
            self.db.query(LessonPlan)
            .filter(LessonPlan.id == lesson_plan_id, LessonPlan.school_id == school_id)
            .first()
        )