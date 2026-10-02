import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.school_class import SchoolClass
from app.models.user import User
from app.schemas.reteach import ConceptPriority
from app.services.concept_priority_service import ConceptPriorityService
from app.services.reteach_recommendation_service import ReteachRecommendationService

from fastapi import Request
from app.core.rate_limit import limiter

router = APIRouter(prefix="/classes", tags=["reteach"])


def _assert_owns_class(db: Session, class_id: uuid.UUID, teacher: User) -> None:
    school_class = (
        db.query(SchoolClass).filter(SchoolClass.id == class_id, SchoolClass.school_id == teacher.school_id).first()
    )
    if school_class is None or school_class.teacher_id != teacher.id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Class not found.")


@router.get(
    "/{class_id}/concept-priorities",
    response_model=list[ConceptPriority],
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def concept_priorities(class_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _assert_owns_class(db, class_id, current_user)
    return ConceptPriorityService(db).get_top_concepts(class_id=class_id)


@router.post("/{class_id}/reteach-recommendations", dependencies=[Depends(require_roles(UserRole.TEACHER))])
@limiter.limit("10/minute")
def reteach_recommendations(request: Request, response: Response, class_id: uuid.UUID, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    _assert_owns_class(db, class_id, current_user)  # ReteachRecommendationService also checks this internally — belt and suspenders
    top_concepts, recommendations = ReteachRecommendationService(db).generate_for_class(class_id=class_id, teacher=current_user)
    by_concept = {r.concept: r for r in recommendations}
    return [
        {"concept": c.concept, "frequency": c.frequency, "recommendation": by_concept.get(c.concept)}
        for c in top_concepts
    ]