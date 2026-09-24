import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import UserRole

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    email: str
    school_id: uuid.UUID | None
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime