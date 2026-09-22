from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.job_description import (
    create_job_description,
    get_job_description_by_id,
    update_job_description_processing,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionResponse,
)
from app.services.job_description_processor import (
    extract_structured_job_description,
)
from app.schemas.skill import (
    ExtractedSkillsResponse,
)

from app.services.skill_processing_service import (
    extract_and_store_job_description_skills,
)


router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"],
)


@router.post(
    "/process",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def process_job_description(
    job_data: JobDescriptionCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    job_description = create_job_description(
        db=db,
        user_id=current_user.id,
        target_job_title=job_data.target_job_title,
        raw_description=job_data.description,
        resume_id=job_data.resume_id,
    )

    try:

        cleaned_text, structured_data = (
            extract_structured_job_description(
                target_job_title=job_data.target_job_title,
                text=job_data.description,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Failed to process job description."
            ),
        )

    updated_job_description = (
        update_job_description_processing(
            db=db,
            job_description=job_description,
            cleaned_description=cleaned_text,
            structured_data=structured_data.model_dump(),
        )
    )

    return updated_job_description


@router.get(
    "/{job_description_id}",
    response_model=JobDescriptionResponse,
)
def get_job_description(
    job_description_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

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

    return job_description

@router.post(
    "/{job_description_id}/skills",
    response_model=ExtractedSkillsResponse,
)
def extract_job_description_skills(
    job_description_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

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

    try:

        skills = (
            extract_and_store_job_description_skills(
                db=db,
                job_description=job_description,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Failed to extract job description skills."
            ),
        )

    return {
        "source_id": job_description.id,
        "source_type": "job_description",
        "skills": skills,
    }