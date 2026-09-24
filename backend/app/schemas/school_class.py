import uuid

from pydantic import BaseModel, ConfigDict, Field

class ClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=100)
    grade: str = Field(min_length=1, max_length=50)
    
class ClassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    school_id: uuid.UUID
    teacher_id: uuid.UUID
    name: str
    subject: str
    grade: str
    student_count: int
    
class EnrollStudentRequest(BaseModel):
    student_id: uuid.UUID