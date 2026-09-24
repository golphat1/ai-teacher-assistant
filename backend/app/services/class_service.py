import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.user import User
from app.repositories.class_repository import ClassRepository
from app.repositories.user_repository import UserRepository


class ClassService:
    def __init__(self, db: Session):
        self.db = db
        self.classes = ClassRepository(db)
        self.users = UserRepository(db)

    def create_class(self, *, teacher: User, name: str, subject: str, grade: str):
        # FIX 1: was get_by_id(...); creating a class means calling create(...)
        school_class = self.classes.create(
            school_id=teacher.school_id,
            teacher_id=teacher.id,
            name=name,
            subject=subject,
            grade=grade,
        )
        self.db.commit()
        self.db.refresh(school_class)
        return school_class

    def get_class_for_teacher(self, *, class_id: uuid.UUID, teacher: User):
        school_class = self.classes.get_by_id(class_id, school_id=teacher.school_id)
        if school_class is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found.")
        if school_class.teacher_id != teacher.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this class.")
        return school_class

    def enroll_student(self, *, class_id: uuid.UUID, teacher: User, student_id: uuid.UUID):
        school_class = self.get_class_for_teacher(class_id=class_id, teacher=teacher)

        student = self.users.get_by_id(student_id)
        if student is None or student.role != UserRole.STUDENT or student.school_id != teacher.school_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found in this school.")

        try:
            # FIX 2: the repository requires school_id as a keyword argument
            enrollment = self.classes.add_enrollment(
                school_class.id, school_id=teacher.school_id, student_id=student.id
            )
            school_class.student_count += 1   # see the check below
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled.")

        self.db.refresh(enrollment)
        return enrollment