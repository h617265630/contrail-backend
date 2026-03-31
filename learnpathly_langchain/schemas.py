from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Intent(BaseModel):
    goal: str = Field(description="Learning goal")
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    focus: list[str] = Field(default_factory=list)
    language: str = "zh"
    time_budget: str = ""


class PlanNode(BaseModel):
    title: str
    description: str
    order: int


class Resource(BaseModel):
    type: Literal["youtube", "github", "doc", "article", "course"]
    title: str
    url: HttpUrl
    description: str
    source_score: float = 0.0
    why_recommended: str = ""


class LearningPathNode(BaseModel):
    title: str
    description: str
    order: int
    resources: list[Resource] = Field(default_factory=list)


class LearningPathOutput(BaseModel):
    title: str
    summary: str
    nodes: list[LearningPathNode]


class LearningPathRequest(BaseModel):
    query: str


class LearningPathResponse(BaseModel):
    data: LearningPathOutput
    warnings: list[str] = Field(default_factory=list)
