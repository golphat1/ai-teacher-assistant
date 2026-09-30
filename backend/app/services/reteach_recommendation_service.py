import uuid

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.ai.providers.base import AIGenerationError
from app.core.config import settings
from app.models.school_class import SchoolClass
from app.repositories.ai_request_log_repository import AIRequestLogRepository
from app.services.ai_budget_service import AIBudgetService
from app.services.concept_priority_service import ConceptPriorityService


class ReteachRecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.priorities = ConceptPriorityService(db)
        self.orchestrator = AIOrchestrator()
        self.ai_logs = AIRequestLogRepository(db)
        self.budget = AIBudgetService(db)

    def generate_for_class(self, *, class_id: uuid.UUID, teacher, limit: int = 5):
        school_class = (
            self.db.query(SchoolClass)
            .filter(SchoolClass.id == class_id, SchoolClass.school_id == teacher.school_id)
            .first()
        )
        if school_class is None or school_class.teacher_id != teacher.id:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Class not found.")

        top_concepts = self.priorities.get_top_concepts(class_id=class_id, limit=limit)
        if not top_concepts:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="No analyzed submissions yet for this class — nothing to prioritize.",
            )

        self.budget.check_budget(teacher.school_id)

        requested_concepts = {c.concept for c in top_concepts}
        model_name = settings.anthropic_model if settings.ai_provider == "anthropic" else settings.openai_model

        try:
            result, usage, provider_name, _ = self.orchestrator.generate_reteach_recommendations(
                [c.model_dump() for c in top_concepts]
            )
        except AIGenerationError as exc:
            self.ai_logs.log(
                school_id=teacher.school_id, user_id=teacher.id, purpose="reteach_recommendation",
                provider=settings.ai_provider, model=model_name, prompt_tokens=0, completion_tokens=0,
                latency_ms=0, status="error", error_message=str(exc),
            )
            self.db.commit()
            raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail="Recommendation generation failed.")

        # Grounding check — same pattern as Stage 9: the AI must not invent or drop a concept.
        returned_concepts = {r.concept for r in result.recommendations}
        if not returned_concepts.issubset(requested_concepts):
            self.ai_logs.log(
                school_id=teacher.school_id, user_id=teacher.id, purpose="reteach_recommendation",
                provider=provider_name, model=model_name, prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"], latency_ms=usage["latency_ms"],
                status="error", error_message="AI referenced a concept not in the prioritized list.",
            )
            self.db.commit()
            raise HTTPException(
                status_code=http_status.HTTP_502_BAD_GATEWAY,
                detail="AI recommendations referenced concepts outside the prioritized list. Please retry.",
            )

        self.ai_logs.log(
            school_id=teacher.school_id, user_id=teacher.id, purpose="reteach_recommendation",
            provider=provider_name, model=model_name, prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"], latency_ms=usage["latency_ms"], status="success",
        )
        self.db.commit()
        return top_concepts, result.recommendations