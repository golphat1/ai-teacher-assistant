import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AssessmentType, QuestionType


class AssessmentQuestionCreate(BaseModel):
    question_text: str = Field(min_length=1)
    question_type: QuestionType
    options: list[str] | None = None
    correct_answer_text: str | None = None
    max_score: float = Field(gt=0)
    order_index: int = 0


class AssessmentCreateRequest(BaseModel):
    lesson_plan_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    assessment_type: AssessmentType = AssessmentType.FORMATIVE
    questions: list[AssessmentQuestionCreate] = Field(min_length=1)


class AssessmentQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question_text: str
    question_type: QuestionType
    options: list[str] | None
    max_score: float
    order_index: int
    # correct_answer_text is deliberately excluded — see note below.


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    lesson_plan_id: uuid.UUID
    title: str
    assessment_type: AssessmentType
    questions: list[AssessmentQuestionRead]