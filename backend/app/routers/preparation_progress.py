from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.job_description import get_job_description_by_id
from app.crud.preparation_plan import (
    get_preparation_plan,
    get_preparation_plan_item,
)
from app.crud.resume import get_resume_by_id
from app.database.database import get_db
from app.models.user import User
from app.schemas.preparation_progress import (
    PreparationProgressResponse,
    PreparationProgressResponseData,
    PreparationProgressUpdate,
)
from app.services.preparation_progress_service import (
    get_preparation_progress,
    update_preparation_progress,
)


router = APIRouter(
    prefix="/preparation-plans",
    tags=["Preparation Progress"],
)


@router.patch(
    "/items/{plan_item_id}/progress",
    response_model=PreparationProgressResponse,
)
def update_progress(
    plan_item_id: int,
    progress_data: PreparationProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan_item = get_preparation_plan_item(
        db=db,
        plan_item_id=plan_item_id,
    )

    if plan_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation plan item not found.",
        )

    plan = plan_item.plan

    resume = get_resume_by_id(
        db=db,
        resume_id=plan.resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    job_description = get_job_description_by_id(
        db=db,
        job_description_id=plan.job_description_id,
        user_id=current_user.id,
    )

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    try:
        progress = update_preparation_progress(
            db=db,
            plan_item=plan_item,
            status=progress_data.status,
            notes=progress_data.notes,
        )

        return progress

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preparation progress.",
        )


@router.get(
    "/resume/{resume_id}/job-description/{job_description_id}/progress",
    response_model=PreparationProgressResponseData,
)
def get_progress(
    resume_id: int,
    job_description_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    job_description = get_job_description_by_id(
        db=db,
        job_description_id=job_description_id,
        user_id=current_user.id,
    )

    if job_description is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    plan = get_preparation_plan(
        db=db,
        resume_id=resume_id,
        job_description_id=job_description_id,
    )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preparation plan not found.",
        )

    try:
        return get_preparation_progress(
            db=db,
            plan=plan,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve preparation progress.",
        )

