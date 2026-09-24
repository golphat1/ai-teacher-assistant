import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.school_class import ClassCreateRequest, ClassRead, EnrollStudentRequest
from app.services.class_service import ClassService

router = APIRouter(prefix="/classes", tags=["classes"])

@router.post(
    "",
    response_model=ClassRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def create_class(
    payload: ClassCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = ClassService(db)
    return service.create_class(
        teacher=current_user, name=payload.name, subject=payload.subject, grade=payload.grade
    )
    
@router.get("/{class_id}", response_model=ClassRead)
def get_class(class_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = ClassService(db)
    return service.get_class_for_teacher(class_id=class_id, teacher=current_user)

@router.post(
    "/{class_id}/enroll",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def enroll_student(
    class_id: uuid.UUID,
    payload: EnrollStudentRequest,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
):
    service = ClassService(db)
    enrollment = service.enroll_student(class_id=class_id, student_id=payload.student_id, teacher=current_user)
    return{"id": str(enrollment.id), "class_id": str(class_id), "student_id": str(payload.student_id)}