import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.submission import StudentSubmission, SubmissionAnswer
from app.models.assignment import AssessmentAssignment
from app.models.school_class import SchoolClass


class SubmissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, assignment_id, student_id, answers: list[dict]) -> StudentSubmission:
        submission = StudentSubmission(
            assignment_id=assignment_id, student_id=student_id, submitted_at=datetime.now(timezone.utc)
        )
        self.db.add(submission)
        self.db.flush()

        for a in answers:
            self.db.add(SubmissionAnswer(submission_id=submission.id, **a))
        self.db.flush()
        return submission

    def get_by_id(self, submission_id: uuid.UUID) -> StudentSubmission | None:
        return (
            self.db.query(StudentSubmission)
            .options(selectinload(StudentSubmission.answers))
            .filter(StudentSubmission.id == submission_id)
            .first()
        )

    def list_for_assignment(self, assignment_id: uuid.UUID) -> list[StudentSubmission]:
        return self.db.query(StudentSubmission).filter(StudentSubmission.assignment_id == assignment_id).all()
    
    def get_by_id_for_school(self, submission_id: uuid.UUID, *, school_id: uuid.UUID) -> StudentSubmission | None:
        return (
            self.db.query(StudentSubmission)
            .join(AssessmentAssignment, StudentSubmission.assignment_id == AssessmentAssignment.id)
            .join(SchoolClass, AssessmentAssignment.class_id == SchoolClass.id)
            .filter(StudentSubmission.id == submission_id, SchoolClass.school_id == school_id)
            .options(selectinload(StudentSubmission.answers))
            .first()
        )