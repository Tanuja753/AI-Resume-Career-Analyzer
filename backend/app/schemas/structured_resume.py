from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None


class EducationItem(BaseModel):
    degree: str | None = None
    institution: str | None = None
    year: str | None = None
    details: str | None = None


class ExperienceItem(BaseModel):
    job_title: str | None = None
    company: str | None = None
    duration: str | None = None
    description: str | None = None


class ProjectItem(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str | None = None
    issuer: str | None = None
    year: str | None = None


class StructuredResume(BaseModel):
    personal_info: PersonalInfo
    education: list[EducationItem] = Field(
        default_factory=list
    )
    skills: list[str] = Field(
        default_factory=list
    )
    experience: list[ExperienceItem] = Field(
        default_factory=list
    )
    projects: list[ProjectItem] = Field(
        default_factory=list
    )
    certifications: list[CertificationItem] = Field(
        default_factory=list
    )
    achievements: list[str] = Field(
        default_factory=list
    )


class StructuredResumeResponse(BaseModel):
    id: int
    original_filename: str
    status: str
    structured_data: StructuredResume