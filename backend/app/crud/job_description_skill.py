from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_description_skill import (
    JobDescriptionSkill,
)


def get_job_description_skill(
    db: Session,
    job_description_id: int,
    skill_id: int,
) -> JobDescriptionSkill | None:

    statement = (
        select(JobDescriptionSkill)
        .where(
            JobDescriptionSkill.job_description_id
            == job_description_id,
            JobDescriptionSkill.skill_id
            == skill_id,
        )
    )

    return db.scalar(statement)


def create_job_description_skill(
    db: Session,
    job_description_id: int,
    skill_id: int,
) -> JobDescriptionSkill:

    job_description_skill = (
        JobDescriptionSkill(
            job_description_id=job_description_id,
            skill_id=skill_id,
            source="structured_job_description",
        )
    )

    db.add(job_description_skill)

    return job_description_skill