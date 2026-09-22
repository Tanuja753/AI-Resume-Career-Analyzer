from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_description import JobDescription


def create_job_description(
    db: Session,
    user_id: int,
    target_job_title: str,
    raw_description: str,
    resume_id: int | None = None,
) -> JobDescription:

    job_description = JobDescription(
        user_id=user_id,
        resume_id=resume_id,
        target_job_title=target_job_title,
        raw_description=raw_description,
        status="created",
    )

    db.add(job_description)
    db.commit()
    db.refresh(job_description)

    return job_description


def get_job_description_by_id(
    db: Session,
    job_description_id: int,
    user_id: int,
) -> JobDescription | None:

    statement = (
        select(JobDescription)
        .where(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id,
        )
    )

    return db.scalar(statement)


def update_job_description_processing(
    db: Session,
    job_description: JobDescription,
    cleaned_description: str,
    structured_data: dict,
) -> JobDescription:

    job_description.cleaned_description = cleaned_description
    job_description.structured_data = structured_data
    job_description.status = "processed"
    job_description.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(job_description)

    return job_description