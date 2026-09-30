import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.assessment import AssessmentCreateRequest, AssessmentRead
from app.services.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.TEACHER))])
def create_assessment(payload: AssessmentCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AssessmentService(db).create_assessment(request=payload, teacher=current_user)


@router.post(
    "/from-lesson-plan/{lesson_plan_id}",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def create_assessment_from_lesson_plan(lesson_plan_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AssessmentService(db).create_from_lesson_content(lesson_plan_id=lesson_plan_id, teacher=current_user)


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(assessment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AssessmentService(db).get_assessment_for_teacher(assessment_id=assessment_id, teacher=current_user)