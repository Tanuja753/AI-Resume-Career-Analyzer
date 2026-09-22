from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_compatibility import JobCompatibility


def get_job_compatibility(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
) -> JobCompatibility | None:

    statement = select(JobCompatibility).where(
        JobCompatibility.resume_id == resume_id,
        JobCompatibility.job_description_id == job_description_id,
    )

    return db.scalar(statement)


def create_job_compatibility(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
    total_required: int,
    matched: int,
    partial: int,
    missing: int,
    skill_coverage_percentage: float,
    semantic_match_percentage: float,
    compatibility_score: float,
    explanation: str,
) -> JobCompatibility:

    compatibility = JobCompatibility(
        resume_id=resume_id,
        job_description_id=job_description_id,
        total_required=total_required,
        matched=matched,
        partial=partial,
        missing=missing,
        skill_coverage_percentage=skill_coverage_percentage,
        semantic_match_percentage=semantic_match_percentage,
        compatibility_score=compatibility_score,
        explanation=explanation,
    )

    db.add(compatibility)

    return compatibility