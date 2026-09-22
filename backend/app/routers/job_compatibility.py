from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.job_description import (
    get_job_description_by_id,
)
from app.crud.resume import get_resume_by_id
from app.database.database import get_db
from app.models.user import User
from app.models.job_compatibility import JobCompatibility
from app.schemas.job_compatibility import (
    JobCompatibilityResponse,
)
from app.services.job_compatibility_service import (
    analyze_job_compatibility,
)


router = APIRouter(
    prefix="/job-compatibility",
    tags=["Job Compatibility"],
)


@router.post(
    "/resume/{resume_id}/job-description/{job_description_id}",
    response_model=JobCompatibilityResponse,
)
def analyze_resume_job_compatibility(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # VALIDATE RESUME OWNERSHIP
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
    # VALIDATE JOB DESCRIPTION OWNERSHIP
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
    # ANALYSIS
    # ---------------------------------------------------------

    try:

        result = analyze_job_compatibility(
            db=db,
            resume=resume,
            job_description=job_description,
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze job compatibility",
        )

@router.get(
    "/resume/{resume_id}/job-description/{job_description_id}",
    response_model=JobCompatibilityResponse,
)
def get_resume_job_compatibility(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------
    # VALIDATE RESUME OWNERSHIP
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
    # VALIDATE JOB DESCRIPTION OWNERSHIP
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
    # GET EXISTING COMPATIBILITY RESULT
    # ---------------------------------------------------------

    compatibility = (
        db.query(JobCompatibility)
        .filter(
            JobCompatibility.resume_id == resume_id,
            JobCompatibility.job_description_id == job_description_id,
        )
        .first()
    )

    if compatibility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compatibility analysis not found",
        )

    return compatibility