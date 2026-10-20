import uuid

from pydantic import BaseModel, Field


class ClauseQuestionRequest(BaseModel):
    clause_id: uuid.UUID
    question: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(default="en", max_length=10)


class ClauseAnswerResponse(BaseModel):
    clause_id: uuid.UUID
    question: str
    answer: str
    confidence: float | None = None
    sources: list[str] = []
