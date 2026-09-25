import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator  # extended below with analyze_submission
from app.ai.providers.base import AIGenerationError
from app.models.enums import SubmissionStatus
from app.models.submission import StudentSubmission, SubmissionAnswer
from app.models.submission_analysis import SubmissionAnalysis
from app.repositories.ai_request_log_repository import AIRequestLogRepository


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_logs = AIRequestLogRepository(db)
        self.orchestrator = AIOrchestrator()

    def analyze_submission(self, *, submission_id: uuid.UUID, teacher):
        submission = (
            self.db.query(StudentSubmission).filter(StudentSubmission.id == submission_id).first()
        )
        if submission is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Submission not found.")

        answers = submission.answers
        real_question_ids = {str(a.question_id) for a in answers}

        try:
            result, usage, provider_name = self.orchestrator.analyze_submission(answers)
        except AIGenerationError as exc:
            raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=f"Analysis failed: {exc}")

        # Anti-hallucination check: reject any question_id the AI invented.
        returned_ids = {pq.question_id for pq in result.per_question_scores}
        if not returned_ids.issubset(real_question_ids):
            raise HTTPException(
                status_code=http_status.HTTP_502_BAD_GATEWAY,
                detail="AI analysis referenced questions not present in this submission. Please retry.",
            )

        for pq in result.per_question_scores:
            answer = next(a for a in answers if str(a.question_id) == pq.question_id)
            answer.score = pq.score

        analysis = SubmissionAnalysis(
            submission_id=submission.id,
            overall_score=result.overall_score,
            feedback_text=result.feedback_text,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            misunderstood_concepts=result.misunderstood_concepts,
            recommendations=result.recommendations,
            ai_provider_used=provider_name,
            analyzed_at=datetime.now(timezone.utc),
        )
        self.db.add(analysis)
        submission.status = SubmissionStatus.ANALYZED
        self.db.commit()
        self.db.refresh(analysis)
        return analysis