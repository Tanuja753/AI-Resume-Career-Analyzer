from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume import Resume


def create_resume(
    db: Session,
    user_id: int,
    original_filename: str,
    stored_filename: str,
    file_path: str,
    content_type: str,
    file_size: int,
) -> Resume:

    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=file_path,
        content_type=content_type,
        file_size=file_size,
        status="uploaded",
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def get_resumes_by_user(
    db: Session,
    user_id: int,
) -> list[Resume]:

    statement = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.uploaded_at.desc())
    )

    return list(db.scalars(statement).all())


def get_resume_by_id(
    db: Session,
    resume_id: int,
    user_id: int,
) -> Resume | None:

    statement = (
        select(Resume)
        .where(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
    )

    return db.scalar(statement)


def update_resume_extraction(
    db: Session,
    resume: Resume,
    extracted_text: str,
) -> Resume:

    resume.extracted_text = extracted_text
    resume.extracted_at = datetime.utcnow()
    resume.status = "extracted"

    db.commit()
    db.refresh(resume)

    return resume

def update_structured_resume(
    db: Session,
    resume: Resume,
    structured_data: dict,
) -> Resume:

    resume.structured_data = structured_data
    resume.structured_at = datetime.utcnow()
    resume.status = "structured"

    db.commit()
    db.refresh(resume)

    return resume