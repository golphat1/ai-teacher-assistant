import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.assessment import Assessment, AssessmentQuestion


class AssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, lesson_plan_id, title, assessment_type, questions: list[dict]) -> Assessment:
        assessment = Assessment(lesson_plan_id=lesson_plan_id, title=title, assessment_type=assessment_type)
        self.db.add(assessment)
        self.db.flush()

        for q in questions:
            self.db.add(AssessmentQuestion(assessment_id=assessment.id, **q))
        self.db.flush()
        return assessment

    def get_by_id(self, assessment_id: uuid.UUID) -> Assessment | None:
        return (
            self.db.query(Assessment)
            .options(selectinload(Assessment.questions))
            .filter(Assessment.id == assessment_id)
            .first()
        )