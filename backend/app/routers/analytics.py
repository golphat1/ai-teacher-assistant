 # backend/app/routers/analytics.py
import uuid
from fastapi import APIRouter, Depends
from app.models import AssessmentAssignment, StudentSubmission, SubmissionAnalysis
from app.auth import get_current_user
from ..database import get_db

router = APIRouter()

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