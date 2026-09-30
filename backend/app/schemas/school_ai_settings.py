import uuid

from pydantic import BaseModel, ConfigDict, Field


class SchoolAISettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    school_id: uuid.UUID
    preferred_provider: str
    preferred_model: str | None
    monthly_token_budget: int | None


class SchoolAISettingsUpdateRequest(BaseModel):
    preferred_provider: str | None = None
    preferred_model: str | None = None
    monthly_token_budget: int | None = Field(default=None, ge=0)