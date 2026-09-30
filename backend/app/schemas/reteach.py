from pydantic import BaseModel, Field


class ConceptPriority(BaseModel):
    concept: str
    frequency: int


class PedagogicalRecommendation(BaseModel):
    concept: str
    why_it_matters: str
    suggested_activity: str
    check_for_understanding: str
    follow_up_resource: str


class ReteachRecommendationAIResult(BaseModel):
    recommendations: list[PedagogicalRecommendation] = Field(min_length=1)