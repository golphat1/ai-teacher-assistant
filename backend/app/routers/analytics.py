 # backend/app/routers/analytics.py
import uuid
from fastapi import APIRouter, Depends
from app.models import AssessmentAssignment, StudentSubmission, SubmissionAnalysis
#from app.auth import get_current_user
#from ..database import get_db
from app.schemas.analytics import ClassAnalyticsOverview, SubmissionTableRow

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.analytics import ClassAnalyticsOverview, SubmissionTableRow
from app.services.analytics_service import AnalyticsService


router = APIRouter(prefix="/classes", tags=["analytics"])

@router.get("/classes/{class_id}/analytics")
def class_analytics(class_id: uuid.UUID, db=Depends(get_db), current_user=Depends(get_current_user)):
    analyses = (
        db.query(SubmissionAnalysis)
        .join(StudentSubmission)
        .join(AssessmentAssignment)
        .filter(AssessmentAssignment.class_id == class_id)
        .all()
    )
    if not analyses:
        return {"average_score": None, "submission_count": 0, "common_misconceptions": []}

    scores = [float(a.overall_score) for a in analyses]
    concept_counts: dict[str, int] = {}
    for a in analyses:
        for concept in a.misunderstood_concepts:
            concept_counts[concept] = concept_counts.get(concept, 0) + 1

    return {
        "average_score": sum(scores) / len(scores),
        "submission_count": len(scores),
        "score_distribution": scores,
        "common_misconceptions": sorted(concept_counts.items(), key=lambda x: -x[1])[:5],
    }
    
@router.get(
    "/{class_id}/analytics",
    response_model=ClassAnalyticsOverview,
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def get_analytics(
    class_id: uuid.UUID,
    refresh: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AnalyticsService(db).get_overview(class_id=class_id, teacher=current_user, force_refresh=refresh)


@router.get(
    "/{class_id}/submissions-table",
    response_model=list[SubmissionTableRow],
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def get_submissions_table(class_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AnalyticsService(db).get_submissions_table(class_id=class_id, teacher=current_user)