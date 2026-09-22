from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeDraftCreate(BaseModel):
    source_resume_id: int

    job_description_id: int | None = None

    title: str = Field(
        default="My Resume",
        min_length=1,
        max_length=200,
    )


class ResumeDraftUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    content: dict


class ResumeDraftResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int
    source_resume_id: int
    job_description_id: int | None
    title: str
    content: dict
    status: str
    created_at: datetime
    updated_at: datetime


class ATSValidationIssue(BaseModel):
    severity: str
    section: str
    message: str


class ATSValidationResponse(BaseModel):
    draft_id: int

    is_valid: bool

    score: float = Field(
        ge=0,
        le=100,
    )

    issues: list[ATSValidationIssue]