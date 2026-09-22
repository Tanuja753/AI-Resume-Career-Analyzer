from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.skill_match import SkillMatch


def delete_skill_matches(
    db: Session,
    resume_id: int,
    job_description_id: int,
) -> None:

    statement = delete(SkillMatch).where(
        SkillMatch.resume_id == resume_id,
        SkillMatch.job_description_id
        == job_description_id,
    )

    db.execute(statement)


def create_skill_match(
    db: Session,
    resume_id: int,
    job_description_id: int,
    resume_skill_id: int | None,
    job_description_skill_id: int,
    match_type: str,
    similarity_score: float | None,
    matching_method: str,
) -> SkillMatch:

    skill_match = SkillMatch(
        resume_id=resume_id,
        job_description_id=job_description_id,
        resume_skill_id=resume_skill_id,
        job_description_skill_id=(
            job_description_skill_id
        ),
        match_type=match_type,
        similarity_score=similarity_score,
        matching_method=matching_method,
    )

    db.add(skill_match)

    return skill_match


def get_skill_matches(
    db: Session,
    resume_id: int,
    job_description_id: int,
) -> list[SkillMatch]:

    statement = (
        select(SkillMatch)
        .where(
            SkillMatch.resume_id == resume_id,
            SkillMatch.job_description_id
            == job_description_id,
        )
        .order_by(
            SkillMatch.id
        )
    )

    return list(
        db.scalars(statement).all()
    )