import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.class_enrollment import ClassEnrollment
from app.models.enums import EnrollmentStatus
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.submission_repository import SubmissionRepository


class SubmissionService:
    def __init__(self, db: Session):
        self.db = db
        self.submissions = SubmissionRepository(db)
        self.assignments = AssignmentRepository(db)
        self.assessments = AssessmentRepository(db)

    def submit(self, *, assignment_id: uuid.UUID, request, student):
        assignment = self.assignments.get_by_id(assignment_id)
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        enrolled = (
            self.db.query(ClassEnrollment)
            .filter(
                ClassEnrollment.class_id == assignment.class_id,
                ClassEnrollment.student_id == student.id,
                ClassEnrollment.status == EnrollmentStatus.ACTIVE,
            )
            .first()
        )
        if enrolled is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not enrolled in this class.")

        assessment = self.assessments.get_by_id(assignment.assessment_id)
        valid_question_ids = {q.id for q in assessment.questions}
        for answer in request.answers:
            if answer.question_id not in valid_question_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Question {answer.question_id} does not belong to this assignment's assessment.",
                )

        answers = [a.model_dump(mode="json") for a in request.answers]
        try:
            submission = self.submissions.create(assignment_id=assignment.id, student_id=student.id, answers=answers)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already submitted this assignment.")

        self.db.refresh(submission)
        return submission

    def list_for_assignment(self, *, assignment_id: uuid.UUID, teacher):
        assignment = self.assignments.get_by_id(assignment_id)
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        if assignment.assigned_by != teacher.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this assignment.")
        return self.submissions.list_for_assignment(assignment_id)