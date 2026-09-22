from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume_draft import ResumeDraft


def create_resume_draft(
    db: Session,
    *,
    user_id: int,
    source_resume_id: int,
    job_description_id: int | None,
    title: str,
    content: dict,
) -> ResumeDraft:

    draft = ResumeDraft(
        user_id=user_id,
        source_resume_id=source_resume_id,
        job_description_id=job_description_id,
        title=title,
        content=content,
        status="draft",
    )

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft


def get_resume_draft_by_id(
    db: Session,
    *,
    draft_id: int,
    user_id: int,
) -> ResumeDraft | None:

    statement = (
        select(ResumeDraft)
        .where(
            ResumeDraft.id == draft_id,
            ResumeDraft.user_id == user_id,
        )
    )

    return db.scalar(statement)


def get_resume_drafts_by_user(
    db: Session,
    *,
    user_id: int,
) -> list[ResumeDraft]:

    statement = (
        select(ResumeDraft)
        .where(
            ResumeDraft.user_id == user_id,
        )
        .order_by(
            ResumeDraft.updated_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def update_resume_draft(
    db: Session,
    *,
    draft: ResumeDraft,
    title: str,
    content: dict,
) -> ResumeDraft:

    draft.title = title
    draft.content = content
    draft.status = "draft"

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft


def delete_resume_draft(
    db: Session,
    *,
    draft: ResumeDraft,
) -> None:

    db.delete(draft)
    db.commit()