from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume_skill import ResumeSkill


def get_resume_skill(
    db: Session,
    resume_id: int,
    skill_id: int,
) -> ResumeSkill | None:

    statement = (
        select(ResumeSkill)
        .where(
            ResumeSkill.resume_id == resume_id,
            ResumeSkill.skill_id == skill_id,
        )
    )

    return db.scalar(statement)


def create_resume_skill(
    db: Session,
    resume_id: int,
    skill_id: int,
) -> ResumeSkill:

    resume_skill = ResumeSkill(
        resume_id=resume_id,
        skill_id=skill_id,
        source="structured_resume",
    )

    db.add(resume_skill)

    return resume_skill