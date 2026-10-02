import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmissionAnswerCreate(BaseModel):
    question_id: uuid.UUID
    answer_text: str = Field(min_length=1, max_length=5000)


class SubmissionCreateRequest(BaseModel):
    answers: list[SubmissionAnswerCreate] = Field(min_length=1)


class SubmissionAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_id: uuid.UUID
    answer_text: str
    score: float | None


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    assignment_id: uuid.UUID
    student_id: uuid.UUID
    status: str
    submitted_at: datetime
    answers: list[SubmissionAnswerRead]
    
class SubmissionAnswerDetailRead(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    question_text: str
    max_score: float
    answer_text: str
    score: float | None

class SubmissionDetailRead(BaseModel):
    id: uuid.UUID
    student_name: str
    status: str
    reviewed_at: datetime | None
    answers: list[SubmissionAnswerDetailRead]