from pydantic import BaseModel


class SkillResponse(BaseModel):
    id: int
    name: str
    normalized_name: str
    category: str


class ExtractedSkillsResponse(BaseModel):
    source_id: int
    source_type: str
    skills: list[SkillResponse]