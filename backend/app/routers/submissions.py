import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.submission import SubmissionCreateRequest, SubmissionDetailRead, SubmissionRead
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/assignments", tags=["submissions"])


@router.post(
    "/{assignment_id}/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.STUDENT))],
)
def submit_assignment(assignment_id: uuid.UUID, payload: SubmissionCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SubmissionService(db).submit(assignment_id=assignment_id, request=payload, student=current_user)


@router.get("/{assignment_id}/submissions", response_model=list[SubmissionRead], dependencies=[Depends(require_roles(UserRole.TEACHER))])
def list_submissions(assignment_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SubmissionService(db).list_for_assignment(assignment_id=assignment_id, teacher=current_user)

@router.get("/{submission_id}/detail", response_model=SubmissionDetailRead, dependencies=[Depends(require_roles(UserRole.TEACHER))])
def get_submission_detail(submission_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return SubmissionService(db).get_detail_for_teacher(submission_id=submission_id, teacher=current_user)