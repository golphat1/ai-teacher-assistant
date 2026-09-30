import uuid

from sqlalchemy.orm import Session

from app.models.assignment import AssessmentAssignment
from app.models.submission import StudentSubmission
from app.models.submission_analysis import SubmissionAnalysis
from app.schemas.reteach import ConceptPriority


class ConceptPriorityService:
    """Pure aggregation — no AI call anywhere in this class. Ranking a concept by how many
    students misunderstood it is an exact, checkable fact; it must never be something an
    LLM 'decides,' even approximately."""

    def __init__(self, db: Session):
        self.db = db

    def get_top_concepts(self, *, class_id: uuid.UUID, limit: int = 5) -> list[ConceptPriority]:
        analyses = (
            self.db.query(SubmissionAnalysis)
            .join(StudentSubmission, SubmissionAnalysis.submission_id == StudentSubmission.id)
            .join(AssessmentAssignment, StudentSubmission.assignment_id == AssessmentAssignment.id)
            .filter(AssessmentAssignment.class_id == class_id)
            .all()
        )

        counts: dict[str, int] = {}
        for analysis in analyses:
            for concept in analysis.misunderstood_concepts:
                counts[concept] = counts.get(concept, 0) + 1

        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [ConceptPriority(concept=concept, frequency=freq) for concept, freq in ranked[:limit]]