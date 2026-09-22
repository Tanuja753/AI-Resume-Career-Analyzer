from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobDescriptionSkill(Base):
    __tablename__ = "job_description_skills"

    id: Mapped[int] = mapped_column(
        primary_key=True,
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

    skill_id: Mapped[int] = mapped_column(
        ForeignKey(
            "skills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        default="structured_job_description",
        nullable=False,
    )

    job_description = relationship(
        "JobDescription",
        back_populates="job_description_skills",
    )

    skill = relationship(
        "Skill",
        back_populates="job_description_skills",
    )