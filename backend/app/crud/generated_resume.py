from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.generated_resume import GeneratedResume


def create_generated_resume(
    db: Session,
    *,
    user_id: int,
    draft_id: int,
    file_name: str,
    file_path: str,
) -> GeneratedResume:

    generated_resume = GeneratedResume(
        user_id=user_id,
        draft_id=draft_id,
        file_name=file_name,
        file_path=file_path,
    )

    db.add(generated_resume)
    db.commit()
    db.refresh(generated_resume)

    return generated_resume


def get_generated_resume_by_id(
    db: Session,
    *,
    generated_resume_id: int,
    user_id: int,
) -> GeneratedResume | None:

    statement = (
        select(GeneratedResume)
        .where(
            GeneratedResume.id == generated_resume_id,
            GeneratedResume.user_id == user_id,
        )
    )

    return db.scalar(statement)


def get_generated_resumes_by_draft(
    db: Session,
    *,
    draft_id: int,
    user_id: int,
) -> list[GeneratedResume]:

    statement = (
        select(GeneratedResume)
        .where(
            GeneratedResume.draft_id == draft_id,
            GeneratedResume.user_id == user_id,
        )
        .order_by(
            GeneratedResume.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )