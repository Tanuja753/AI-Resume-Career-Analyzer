from pydantic import BaseModel, Field


class JobCompatibilityResponse(BaseModel):
    id: int
    resume_id: int
    job_description_id: int

    total_required: int
    matched: int
    partial: int
    missing: int

    skill_coverage_percentage: float = Field(
        ge=0,
        le=100,
    )

    semantic_match_percentage: float = Field(
        ge=0,
        le=100,
    )

    compatibility_score: float = Field(
        ge=0,
        le=100,
    )

    explanation: str