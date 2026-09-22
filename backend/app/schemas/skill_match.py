from pydantic import BaseModel, Field


class SkillMatchResponse(BaseModel):

    job_skill: str

    resume_skill: str | None = None

    match_type: str

    similarity_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    matching_method: str


class SkillMatchingResponse(BaseModel):

    resume_id: int

    job_description_id: int

    exact_matches: list[SkillMatchResponse]

    semantic_matches: list[SkillMatchResponse]