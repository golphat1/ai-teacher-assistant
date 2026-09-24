import uuid

from sqlalchemy.orm import Session

from app.models.class_enrollment import ClassEnrollment
from app.models.school_class import SchoolClass

class ClassRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, school_id: uuid.UUID, teacher_id: uuid.UUID, name: str, subject: str, grade: str) -> SchoolClass:
        obj = SchoolClass(school_id=school_id, teacher_id=teacher_id, name=name, subject=subject, grade=grade)
        self.db.add(obj)
        self.db.flush()
        return obj

    def get_by_id(self, class_id: uuid.UUID, *, school_id: uuid.UUID) -> SchoolClass | None:
        return (
            self.db.query(SchoolClass)
            .filter(SchoolClass.id == class_id, SchoolClass.school_id == school_id)
            .first()
        )
        
    def list_for_teachers(self, teacher_id: uuid.UUID, *, school_id: uuid.UUID) -> list[SchoolClass]:
            return (
                self.db.query(SchoolClass)
                .filter(SchoolClass.teacher == teacher_id, SchoolClass.school_id == school_id)
                .all()
            )
            
    def add_enrollment(self, class_id: uuid.UUID, *, school_id: uuid.UUID, student_id: uuid.UUID) -> ClassEnrollment:
        enrollment = ClassEnrollment(class_id=class_id, student_id=student_id)
        self.db.add(enrollment)
        self.db.flush()
        return enrollment