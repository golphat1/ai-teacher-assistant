import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session, selectinload

from app.ai.orchestrator import AIOrchestrator
from app.ai.providers.base import AIGenerationError
from app.core.config import settings
from app.models.assessment import AssessmentQuestion
from app.models.enums import SubmissionStatus
from app.models.submission import StudentSubmission
from app.models.submission_analysis import SubmissionAnalysis
from app.repositories.ai_request_log_repository import AIRequestLogRepository
from app.services.ai_budget_service import AIBudgetService


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.orchestrator = AIOrchestrator()
        self.ai_logs = AIRequestLogRepository(db)
        self.budget = AIBudgetService(db)

    def analyze_submission(self, *, submission_id: uuid.UUID, teacher):
        submission = (
            self.db.query(StudentSubmission)
            .options(selectinload(StudentSubmission.answers))
            .filter(StudentSubmission.id == submission_id)
            .first()
        )
        if submission is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Submission not found.")
        if submission.assignment.assigned_by != teacher.id:
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="You do not own this assignment.")

        answers = submission.answers
        real_question_ids = {str(a.question_id) for a in answers}

        questions_with_answers = []
        for answer in answers:
            question = self.db.get(AssessmentQuestion, answer.question_id)
            questions_with_answers.append(
                {
                    "question_id": str(answer.question_id),
                    "question_text": question.question_text,
                    "correct_answer_text": question.correct_answer_text,
                    "max_score": float(question.max_score),
                    "answer_text": answer.answer_text,
                }
            )

        model_name = settings.anthropic_model if settings.ai_provider == "anthropic" else settings.openai_model
        self.budget.check_budget(teacher.school_id)

        try:
            result, usage, provider_name, _ = self.orchestrator.analyze_submission(questions_with_answers)
        except AIGenerationError as exc:
            self.ai_logs.log(
                school_id=teacher.school_id, user_id=teacher.id, purpose="submission_analysis",
                provider=settings.ai_provider, model=model_name, prompt_tokens=0, completion_tokens=0,
                latency_ms=0, status="error", error_message=str(exc),
            )
            self.db.commit()
            raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail="Analysis failed. Please try again.")

        # --- Grounding check: the anti-hallucination gate ---
        returned_ids = {pq.question_id for pq in result.per_question_scores}
        if not returned_ids.issubset(real_question_ids):
            self.ai_logs.log(
                school_id=teacher.school_id, user_id=teacher.id, purpose="submission_analysis",
                provider=provider_name, model=model_name, prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"], latency_ms=usage["latency_ms"],
                status="error", error_message="AI referenced question_id(s) not present in submission.",
            )
            self.db.commit()
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

        self.ai_logs.log(
            school_id=teacher.school_id, user_id=teacher.id, purpose="submission_analysis",
            provider=provider_name, model=model_name, prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"], latency_ms=usage["latency_ms"], status="success",
        )
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_analysis(self, *, submission_id: uuid.UUID, requester):
        analysis = self.db.query(SubmissionAnalysis).filter(SubmissionAnalysis.submission_id == submission_id).first()
        if analysis is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
        return analysis