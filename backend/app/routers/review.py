import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.review import (
    ScoreOverrideRead,
    ScoreOverrideRequest,
    SubmissionResultsRead,
    SubmissionReviewRead,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix="/submissions", tags=["review"])


@router.patch(
    "/{submission_id}/answers/{answer_id}/override-score",
    response_model=ScoreOverrideRead,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def override_score(
    submission_id: uuid.UUID, answer_id: uuid.UUID, payload: ScoreOverrideRequest,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return ReviewService(db).override_score(
        submission_id=submission_id, answer_id=answer_id, new_score=payload.new_score, reason=payload.reason, teacher=current_user
    )


@router.post(
    "/{submission_id}/review",
    response_model=SubmissionReviewRead,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def mark_reviewed(submission_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ReviewService(db).mark_reviewed(submission_id=submission_id, teacher=current_user)


@router.get(
    "/{submission_id}/results",
    response_model=SubmissionResultsRead,
    dependencies=[Depends(require_roles(UserRole.STUDENT))],
)
def get_results(submission_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ReviewService(db).get_results_for_student(submission_id=submission_id, student=current_user)