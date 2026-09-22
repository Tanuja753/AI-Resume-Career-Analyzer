from datetime import datetime

from pydantic import BaseModel, Field


class JobDescriptionCreate(BaseModel):
    target_job_title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str = Field(
        min_length=50,
        max_length=30000,
    )

    resume_id: int | None = None


class JobDescriptionStructured(BaseModel):
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    experience_required: str | None = None
    education_required: str | None = None

    responsibilities: list[str] = Field(
        default_factory=list
    )

    qualifications: list[str] = Field(
        default_factory=list
    )

    other_requirements: list[str] = Field(
        default_factory=list
    )


class JobDescriptionResponse(BaseModel):
    id: int
    target_job_title: str
    raw_description: str
    cleaned_description: str | None
    structured_data: JobDescriptionStructured | None
    status: str
    created_at: datetime
    processed_at: datetime | None