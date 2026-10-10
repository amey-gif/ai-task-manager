from pydantic import BaseModel, Field


class GenerateDescriptionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class GenerateDescriptionResponse(BaseModel):
    title: str
    description: str


class SummarizeResponse(BaseModel):
    task_id: int
    summary: str


# These two check the JSON that comes BACK from the AI
class AIDescription(BaseModel):
    description: str = Field(min_length=10)


class AISummary(BaseModel):
    summary: str = Field(min_length=5)