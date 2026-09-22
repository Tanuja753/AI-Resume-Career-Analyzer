from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PreparationProgressStatus = Literal[
    "not_started",
    "in_progress",
    "completed",
]


class PreparationProgressUpdate(BaseModel):
    status: PreparationProgressStatus
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class PreparationProgressResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    plan_item_id: int
    status: PreparationProgressStatus
    notes: str | None
    completed_at: datetime | None


class PreparationProgressItemResponse(BaseModel):
    plan_item_id: int
    skill: str
    priority: str
    topic: str
    description: str
    action: str
    estimated_hours: int

    status: PreparationProgressStatus
    notes: str | None
    completed_at: datetime | None


class PreparationProgressSummary(BaseModel):
    total_items: int
    not_started: int
    in_progress: int
    completed: int
    progress_percentage: float


class PreparationProgressResponseData(BaseModel):
    resume_id: int
    job_description_id: int
    plan_id: int

    summary: PreparationProgressSummary

    items: list[PreparationProgressItemResponse]