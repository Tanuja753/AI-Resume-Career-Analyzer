from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.skill_gap import SkillGap


def delete_skill_gaps(
    db: Session,
    resume_id: int,
    job_description_id: int,
) -> None:

    statement = delete(SkillGap).where(
        SkillGap.resume_id == resume_id,
        SkillGap.job_description_id == job_description_id,
    )

    db.execute(statement)


def create_skill_gap(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
    job_description_skill_id: int,
    resume_skill_id: int | None,
    gap_type: str,
    similarity_score: float | None,
    reason: str,
) -> SkillGap:

    skill_gap = SkillGap(
        resume_id=resume_id,
        job_description_id=job_description_id,
        job_description_skill_id=job_description_skill_id,
        resume_skill_id=resume_skill_id,
        gap_type=gap_type,
        similarity_score=similarity_score,
        reason=reason,
    )

    db.add(skill_gap)

    return skill_gap


def get_skill_gaps(
    db: Session,
    resume_id: int,
    job_description_id: int,
) -> list[SkillGap]:

    statement = (
        select(SkillGap)
        .where(
            SkillGap.resume_id == resume_id,
            SkillGap.job_description_id == job_description_id,
        )
        .order_by(SkillGap.id)
    )

    return list(db.scalars(statement).all())