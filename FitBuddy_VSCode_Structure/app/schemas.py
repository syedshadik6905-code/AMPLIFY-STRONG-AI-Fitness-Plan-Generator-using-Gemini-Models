# Pydantic request schemas
from pydantic import BaseModel, Field


class UserInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    age: int = Field(..., ge=16, le=100)
    weight: float = Field(..., gt=0, le=500)
    goal: str = Field(..., min_length=1)
    intensity: str = Field(..., min_length=1)


class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str = Field(..., min_length=1)