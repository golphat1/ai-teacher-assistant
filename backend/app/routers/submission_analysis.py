import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.submission_analysis import SubmissionAnalysisRead
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/submissions", tags=["submission-analysis"])


@router.post(
    "/{submission_id}/analyze",
    response_model=SubmissionAnalysisRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def analyze_submission(submission_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalysisService(db).analyze_submission(submission_id=submission_id, teacher=current_user)


@router.get("/{submission_id}/analysis", response_model=SubmissionAnalysisRead)
def get_analysis(submission_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalysisService(db).get_analysis(submission_id=submission_id, requester=current_user)