import uuid

from sqlalchemy.orm import Session

from app.models.assignment import AssessmentAssignment


class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, assessment_id, class_id, assigned_by, due_at) -> AssessmentAssignment:
        assignment = AssessmentAssignment(
            assessment_id=assessment_id, class_id=class_id, assigned_by=assigned_by, due_at=due_at
        )
        self.db.add(assignment)
        self.db.flush()
        return assignment

    def get_by_id(self, assignment_id: uuid.UUID) -> AssessmentAssignment | None:
        return self.db.query(AssessmentAssignment).filter(AssessmentAssignment.id == assignment_id).first()