import uuid
from datetime import datetime

from pydantic import BaseModel


class MisconceptionFrequency(BaseModel):
    concept: str
    frequency: int


class ClassAnalyticsOverview(BaseModel):
    average_score: float | None
    submission_count: int
    score_distribution: list[float]
    common_misconceptions: list[MisconceptionFrequency]
    generated_at: datetime
    is_cached: bool


class SubmissionTableRow(BaseModel):
    submission_id: uuid.UUID
    student_name: str
    assignment_title: str
    status: str
    review_status: str  # not_analyzed | pending | reviewed | auto_released
    overall_score: float | None
    submitted_at: datetime
    reviewed_at: datetime | None