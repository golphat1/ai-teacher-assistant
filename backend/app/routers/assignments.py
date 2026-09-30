from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.assignment import AssignmentCreateRequest, AssignmentRead
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(UserRole.TEACHER))])
def create_assignment(payload: AssignmentCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AssignmentService(db).create_assignment(request=payload, teacher=current_user)