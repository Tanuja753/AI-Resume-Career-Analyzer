from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobCompatibility(Base):
    __tablename__ = "job_compatibilities"

    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "job_description_id",
            name="uq_job_compatibility_resume_jd",
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

    total_required: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    matched: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    partial: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    missing: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    skill_coverage_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    semantic_match_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    compatibility_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    resume = relationship("Resume")

    job_description = relationship("JobDescription")