from pydantic import BaseModel


class SkillGapItem(BaseModel):

    id: int

    job_skill: str

    resume_skill: str | None = None

    gap_type: str

    similarity_score: float | None = None

    reason: str


class SkillGapSummary(BaseModel):

    total_required: int

    matched: int

    partial: int

    missing: int


class SkillGapAnalysisResponse(BaseModel):

    resume_id: int

    job_description_id: int

    matched_skills: list[SkillGapItem]

    partial_skills: list[SkillGapItem]

    missing_skills: list[SkillGapItem]

    summary: SkillGapSummary