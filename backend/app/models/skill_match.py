from sqlalchemy import (
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


class SkillMatch(Base):

    __tablename__ = "skill_matches"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_description_id: Mapped[int] = mapped_column(
        ForeignKey(
            "job_descriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    resume_skill_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "resume_skills.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    job_description_skill_id: Mapped[int] = mapped_column(
        ForeignKey(
            "job_description_skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    match_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    matching_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    resume = relationship(
        "Resume",
    )

    job_description = relationship(
        "JobDescription",
    )

    resume_skill = relationship(
        "ResumeSkill",
    )

    job_description_skill = relationship(
        "JobDescriptionSkill",
    )