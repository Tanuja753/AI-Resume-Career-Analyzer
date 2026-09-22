from sqlalchemy import (
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base


class SkillGap(Base):

    __tablename__ = "skill_gaps"

    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "job_description_id",
            "job_description_skill_id",
            name="uq_skill_gap_resume_jd_skill",
        ),
    )

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

    job_description_skill_id: Mapped[int] = mapped_column(
        ForeignKey(
            "job_description_skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    resume_skill_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "resume_skills.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    gap_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reason: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    job_description_skill = relationship(
        "JobDescriptionSkill",
    )

    resume_skill = relationship(
        "ResumeSkill",
    )

    resume = relationship(
        "Resume",
    )

    job_description = relationship(
        "JobDescription",
    )