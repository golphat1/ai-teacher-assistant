import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.schemas.assessment import AssessmentRead


class AssignmentCreateRequest(BaseModel):
    assessment_id: uuid.UUID
    class_id: uuid.UUID
    due_at: datetime | None = None


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    assessment_id: uuid.UUID
    class_id: uuid.UUID
    due_at: datetime | None
    
class AssignmentWithAssessmentRead(AssignmentRead):
    assessment: AssessmentRead