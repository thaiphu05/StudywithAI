from pydantic import BaseModel, Field


class CriterionFeedback(BaseModel):
    criterion: str
    band: float = Field(ge=0, le=9)
    explanation: str


class EvaluationResult(BaseModel):
    overall_band: float = Field(ge=0, le=9)
    summary: str
    criteria: list[CriterionFeedback]
    estimated_tokens_used: int
