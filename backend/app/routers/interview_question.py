from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_current_user
from app.crud.job_description import (
    get_job_description_by_id,
)
from app.crud.resume import get_resume_by_id
from app.database.database import get_db
from app.models.user import User
from app.models.interview_question import InterviewQuestion
from app.schemas.interview_question import (
    InterviewQuestionGenerationResponse,
    InterviewQuestionResponse,
)
from app.services.interview_question_service import (
    generate_interview_questions,
)
from app.services.ollama_service import (
    OllamaUnavailableError,
)


router = APIRouter(
    prefix="/interview-questions",
    tags=["Interview Questions"],
)


@router.post(
    "/resume/{resume_id}/job-description/{job_description_id}",
    response_model=InterviewQuestionGenerationResponse,
)
def generate_questions(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # RESUME OWNERSHIP
    # ---------------------------------------------------------

    resume = get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # ---------------------------------------------------------
    # JOB DESCRIPTION OWNERSHIP
    # ---------------------------------------------------------

    job_description = get_job_description_by_id(
        db=db,
        job_description_id=job_description_id,
        user_id=current_user.id,
    )

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    # ---------------------------------------------------------
    # RESUME STRUCTURE CHECK
    # ---------------------------------------------------------

    if not resume.structured_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume structure has not been "
                "generated yet."
            ),
        )

    # ---------------------------------------------------------
    # JOB DESCRIPTION CHECK
    # ---------------------------------------------------------

    if not job_description.structured_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Job description has not been "
                "processed yet."
            ),
        )

    # ---------------------------------------------------------
    # SKILL-GAP DATA
    # ---------------------------------------------------------

    from sqlalchemy import select

    from app.models.skill_gap import SkillGap

    statement = select(SkillGap).where(
        SkillGap.resume_id == resume.id,
        SkillGap.job_description_id
        == job_description.id,
    )

    skill_gaps = list(
        db.scalars(statement).all()
    )

    if not skill_gaps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Skill gap analysis has not been "
                "completed yet."
            ),
        )

    matched_skills = []
    partial_skills = []
    missing_skills = []

    for gap in skill_gaps:

        job_skill_name = (
            gap.job_description_skill
            .skill
            .name
        )

        if gap.gap_type == "matched":

            matched_skills.append(
                job_skill_name
            )

        elif gap.gap_type == "partial":

            partial_skills.append(
                job_skill_name
            )

        elif gap.gap_type == "missing":

            missing_skills.append(
                job_skill_name
            )

    # ---------------------------------------------------------
    # GENERATE QUESTIONS
    # ---------------------------------------------------------

    try:

        questions = (
            generate_interview_questions(
                db=db,
                resume=resume,
                job_description=job_description,
                matched_skills=matched_skills,
                partial_skills=partial_skills,
                missing_skills=missing_skills,
            )
        )

    except OllamaUnavailableError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to generate interview "
                "questions."
            ),
        )

    return {
        "resume_id": resume.id,
        "job_description_id": job_description.id,
        "questions": [
            InterviewQuestionResponse.model_validate(
                question,
                from_attributes=True,
            )
            for question in questions
        ],
    }


@router.get(
    "/resume/{resume_id}/job-description/{job_description_id}/count"
)
def get_interview_question_count(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # RESUME OWNERSHIP
    # ---------------------------------------------------------

    resume = get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # ---------------------------------------------------------
    # JOB DESCRIPTION OWNERSHIP
    # ---------------------------------------------------------

    job_description = get_job_description_by_id(
        db=db,
        job_description_id=job_description_id,
        user_id=current_user.id,
    )

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    # ---------------------------------------------------------
    # COUNT QUESTIONS
    # ---------------------------------------------------------

    question_count = (
        db.query(func.count(InterviewQuestion.id))
        .filter(
            InterviewQuestion.resume_id == resume_id,
            InterviewQuestion.job_description_id
            == job_description_id,
        )
        .scalar()
    )

    return {
        "resume_id": resume_id,
        "job_description_id": job_description_id,
        "question_count": question_count or 0,
    }


@router.get(
    "/resume/{resume_id}/job-description/{job_description_id}"
)
def get_interview_questions(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # RESUME OWNERSHIP
    # ---------------------------------------------------------

    resume = get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # ---------------------------------------------------------
    # JOB DESCRIPTION OWNERSHIP
    # ---------------------------------------------------------

    job_description = get_job_description_by_id(
        db=db,
        job_description_id=job_description_id,
        user_id=current_user.id,
    )

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    # ---------------------------------------------------------
    # GET SAVED QUESTIONS
    # ---------------------------------------------------------

    questions = (
        db.query(InterviewQuestion)
        .filter(
            InterviewQuestion.resume_id == resume_id,
            InterviewQuestion.job_description_id
            == job_description_id,
        )
        .order_by(InterviewQuestion.id)
        .all()
    )

    return {
        "resume_id": resume_id,
        "job_description_id": job_description_id,
        "questions": [
            InterviewQuestionResponse.model_validate(
                question,
                from_attributes=True,
            )
            for question in questions
        ],
    }