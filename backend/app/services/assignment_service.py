from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.school_class import SchoolClass
from app.repositories.assignment_repository import AssignmentRepository
from app.services.assessment_service import AssessmentService
from app.models.class_enrollment import ClassEnrollment
from app.models.enums import EnrollmentStatus, UserRole


class AssignmentService:
    def __init__(self, db: Session):
        self.db = db
        self.assignments = AssignmentRepository(db)
        self.assessment_service = AssessmentService(db)

    def create_assignment(self, *, request, teacher):
        assessment = self.assessment_service.get_assessment_for_teacher(assessment_id=request.assessment_id, teacher=teacher)

        school_class = (
            self.db.query(SchoolClass)
            .filter(SchoolClass.id == request.class_id, SchoolClass.school_id == teacher.school_id)
            .first()
        )
        if school_class is None or school_class.teacher_id != teacher.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")

        assignment = self.assignments.create(
            assessment_id=assessment.id, class_id=school_class.id, assigned_by=teacher.id, due_at=request.due_at
        )
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_for_submission(self, *, assignment_id, user):
        assignment = self.assignments.get_by_id(assignment_id)
        if assignment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")

        if user.role == UserRole.TEACHER:
            if assignment.assigned_by != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this assignment.")
        else:  # student
            enrolled = (
                self.db.query(ClassEnrollment)
                .filter(
                    ClassEnrollment.class_id == assignment.class_id,
                    ClassEnrollment.student_id == user.id,
                    ClassEnrollment.status == EnrollmentStatus.ACTIVE,
                )
                .first()
            )
            if enrolled is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not enrolled in this class.")

        assessment = self.assessment_service.assessments.get_by_id(assignment.assessment_id)
        return assignment, assessment