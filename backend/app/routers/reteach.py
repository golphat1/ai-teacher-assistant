import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.reteach import ConceptPriority, PedagogicalRecommendation
from app.services.concept_priority_service import ConceptPriorityService
from app.services.reteach_recommendation_service import ReteachRecommendationService

router = APIRouter(prefix="/classes", tags=["reteach"])


@router.get(
    "/{class_id}/concept-priorities",
    response_model=list[ConceptPriority],
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def concept_priorities(class_id: uuid.UUID, db: Session = Depends(get_db)):
    return ConceptPriorityService(db).get_top_concepts(class_id=class_id)


@router.post(
    "/{class_id}/reteach-recommendations",
    dependencies=[Depends(require_roles(UserRole.TEACHER))],
)
def reteach_recommendations(class_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    top_concepts, recommendations = ReteachRecommendationService(db).generate_for_class(class_id=class_id, teacher=current_user)
    by_concept = {r.concept: r for r in recommendations}
    return [
        {"concept": c.concept, "frequency": c.frequency, "recommendation": by_concept.get(c.concept)}
        for c in top_concepts
    ]