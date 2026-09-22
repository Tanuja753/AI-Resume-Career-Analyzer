from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PreparationPriority = Literal[
    "high",
    "medium",
    "low",
]


class GeneratedPreparationItem(BaseModel):
    skill: str = Field(
        min_length=1,
        max_length=100,
    )

    priority: PreparationPriority

    topic: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str = Field(
        min_length=10,
        max_length=1000,
    )

    action: str = Field(
        min_length=10,
        max_length=1000,
    )

    estimated_hours: int = Field(
        ge=1,
        le=40,
    )


class GeneratedPreparationPlan(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
    )

    summary: str = Field(
        min_length=20,
        max_length=2000,
    )

    estimated_days: int = Field(
        ge=1,
        le=90,
    )

    items: list[GeneratedPreparationItem] = Field(
        min_length=1,
        max_length=20,
    )


class PreparationPlanItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    plan_id: int
    skill: str
    priority: PreparationPriority
    topic: str
    description: str
    action: str
    estimated_hours: int


class PreparationPlanResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    resume_id: int
    job_description_id: int
    title: str
    summary: str
    estimated_days: int
    items: list[PreparationPlanItemResponse]