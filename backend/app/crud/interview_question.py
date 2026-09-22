from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion


def delete_interview_questions(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
) -> None:

    statement = delete(
        InterviewQuestion
    ).where(
        InterviewQuestion.resume_id == resume_id,
        InterviewQuestion.job_description_id
        == job_description_id,
    )

    db.execute(statement)


def create_interview_question(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
    category: str,
    question: str,
    difficulty: str,
    source: str,
) -> InterviewQuestion:

    interview_question = InterviewQuestion(
        resume_id=resume_id,
        job_description_id=job_description_id,
        category=category,
        question=question,
        difficulty=difficulty,
        source=source,
    )

    db.add(interview_question)

    return interview_question


def get_interview_questions(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
) -> list[InterviewQuestion]:

    statement = (
        select(InterviewQuestion)
        .where(
            InterviewQuestion.resume_id == resume_id,
            InterviewQuestion.job_description_id
            == job_description_id,
        )
        .order_by(InterviewQuestion.id)
    )

    return list(
        db.scalars(statement).all()
    )