from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.lesson_plan import LessonPlanGenerateRequest, LessonPlanGenerateResponse
from app.services.lesson_plan_service import LessonPlanService

router = APIRouter(prefix="/api/v1/lesson-plans", tags=["lesson-plans"])


@router.post(
    "/generate",
    response_model=LessonPlanGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def generate_lesson_plan(
    payload: LessonPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = LessonPlanService(db)
    return service.generate(request=payload, teacher=current_user)