import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScoreOverrideRequest(BaseModel):
    new_score: float = Field(ge=0)
    reason: str | None = Field(default=None, max_length=1000)


class ScoreOverrideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    submission_answer_id: uuid.UUID
    previous_score: float | None
    new_score: float
    overridden_by: uuid.UUID
    reason: str | None
    created_at: datetime


class SubmissionReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: str
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None


class SubmissionResultsRead(BaseModel):
    is_released: bool
    message: str | None = None
    overall_score: float | None = None
    feedback_text: str | None = None
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    recommendations: list[str] | None = None