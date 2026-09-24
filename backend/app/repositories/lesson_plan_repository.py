import uuid
from datetime import datetime

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
            is_mock=is_mock,
            ai_provider_used=None,
            ai_model_used=None,
            generated_at=datetime.utcnow(),
            **content_fields,
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