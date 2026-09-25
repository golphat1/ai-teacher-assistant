from pydantic import BaseModel


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