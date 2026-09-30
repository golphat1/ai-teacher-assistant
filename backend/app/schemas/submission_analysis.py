import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PerQuestionScore(BaseModel):
    question_id: str  # must match a real question_id from the submission — validated below
    score: float
    comment: str


class SubmissionAnalysisAIResult(BaseModel):
    overall_score: float
    per_question_scores: list[PerQuestionScore]
    strengths: list[str]
    weaknesses: list[str]
    misunderstood_concepts: list[str]
    feedback_text: str
    recommendations: list[str]
    
class SubmissionAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    submission_id: uuid.UUID
    overall_score: float
    feedback_text: str
    strengths: list[str]
    weaknesses: list[str]
    misunderstood_concepts: list[str]
    recommendations: list[str]
    ai_provider_used: str
    analyzed_at: datetime