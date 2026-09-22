from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.job_description import (
    get_job_description_by_id,
)
from app.crud.preparation_plan import (
    get_preparation_plan,
)
from app.crud.resume import get_resume_by_id
from app.database.database import get_db
from app.models.user import User
from app.schemas.preparation_plan import (
    PreparationPlanResponse,
)
from app.services.preparation_plan_service import (
    generate_preparation_plan,
)


router = APIRouter(
    prefix="/preparation-plans",
    tags=["Preparation Plans"],
)


@router.post(
    "/resume/{resume_id}/job-description/{job_description_id}",
    response_model=PreparationPlanResponse,
)
def generate_plan(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # Validate resume ownership
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
    # Validate job description ownership
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
    # Validate prerequisites
    # ---------------------------------------------------------

    if not resume.structured_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume structure has not been "
                "generated yet."
            ),
        )

    if not job_description.structured_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Job description has not been "
                "processed yet."
            ),
        )

    # ---------------------------------------------------------
    # Generate preparation plan
    # ---------------------------------------------------------

    try:

        plan = generate_preparation_plan(
            db=db,
            resume=resume,
            job_description=job_description,
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to generate "
                "preparation plan."
            ),
        )

    # ---------------------------------------------------------
    # Return plan with items
    # ---------------------------------------------------------

    return plan


@router.get(
    "/resume/{resume_id}/job-description/{job_description_id}",
    response_model=PreparationPlanResponse,
)
def get_plan(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ---------------------------------------------------------
    # Validate resume ownership
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
    # Validate job description ownership
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
    # Get plan
    # ---------------------------------------------------------

    plan = get_preparation_plan(
        db=db,
        resume_id=resume_id,
        job_description_id=job_description_id,
    )

    if plan is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation plan not found",
        )

    return plan