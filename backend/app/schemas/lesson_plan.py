import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class LessonPlanGenerateRequest(BaseModel):
    class_id: uuid.UUID | None = None
    grade: str = Field(min_length=1, max_length=50)
    subject: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=2, max_length=255)
    student_count: int = Field(gt=0, le=200)
    duration_minutes: int = Field(gt=0, le=300)
    curriculum: str | None = Field(default=None, min_length=1, max_length=50)
    ability_level: str = Field(min_length=1, max_length=50)
    learning_context: str | None = Field(default=None, max_length=100)
    additional_instructions: str | None = Field(default=None, max_length=2000)
    
class TeachingActivity(BaseModel):
    title: str
    teacher_actions: str = Field(description="What the teacher specifically does during this activity.")
    student_actions: str = Field(description="What students specifically do during this activity.")
    duration_minutes: int
    
class DifferentiatedActivity(BaseModel):
    target_group: str
    description: str
    
class AssessmentQuestion(BaseModel):
    question_text: str
    question_type: str
    options: list[str] | None = None
    max_score: float
    
class RubricPerformanceLevel(BaseModel):
    level: str  # e.g. "Exemplary", "Proficient", "Developing", "Beginning"
    descriptor: str = Field(description="What a response at this level actually looks like.")
    points: float


class RubricCriterion(BaseModel):
    criterion: str
    description: str
    max_points: float
    performance_levels: list[RubricPerformanceLevel] = Field(min_length=2)
    
class LessonPlanGenerateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    lesson_plan_id: uuid.UUID
    status: str
    is_mock: bool
    
    grade: str
    subject: str
    topic: str
    student_count: int
    duration_minutes: int
    
    learning_objectives: list[str]
    teaching_activities: list[TeachingActivity]
    differentiated_activities: list[DifferentiatedActivity]
    assessment_questions: list[AssessmentQuestion]
    marking_rubric: list[RubricCriterion]
    homework: list[str]
    revision_questions: list[str]
    
    generated_at: datetime
    
class LessonContentAIResult(BaseModel):
    learning_objectives: list[str]
    teaching_activities: list[TeachingActivity]
    differentiated_activities: list[DifferentiatedActivity]
    assessment_questions: list[AssessmentQuestion]
    marking_rubric: list[RubricCriterion]
    homework: list[str]
    revision_questions: list[str]