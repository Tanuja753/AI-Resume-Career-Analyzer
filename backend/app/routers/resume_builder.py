from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.job_description import get_job_description_by_id
from app.crud.resume import get_resume_by_id
from app.crud.resume_draft import (
    create_resume_draft,
    delete_resume_draft,
    get_resume_draft_by_id,
    get_resume_drafts_by_user,
    update_resume_draft,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.resume_draft import (
    ATSValidationResponse,
    ResumeDraftCreate,
    ResumeDraftResponse,
    ResumeDraftUpdate,
)
from app.services.resume_builder_service import (
    build_initial_resume_content,
    validate_resume_for_ats,
)


router = APIRouter(
    prefix="/resume-builder",
    tags=["Resume Builder"],
)


# ============================================================
# CREATE DRAFT
# ============================================================

@router.post(
    "/drafts",
    response_model=ResumeDraftResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_draft(
    draft_data: ResumeDraftCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    resume = get_resume_by_id(
        db=db,
        resume_id=draft_data.source_resume_id,
        user_id=current_user.id,
    )

    if resume is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    if not resume.structured_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume must be structurally extracted "
                "before creating a resume draft."
            ),
        )

    # --------------------------------------------
    # Validate optional job description
    # --------------------------------------------

    if draft_data.job_description_id is not None:

        job_description = get_job_description_by_id(
            db=db,
            job_description_id=draft_data.job_description_id,
            user_id=current_user.id,
        )

        if job_description is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found.",
            )

    # --------------------------------------------
    # Build initial resume content
    # --------------------------------------------

    content = build_initial_resume_content(
        resume.structured_data
    )

    try:

        draft = create_resume_draft(
            db=db,
            user_id=current_user.id,
            source_resume_id=resume.id,
            job_description_id=draft_data.job_description_id,
            title=draft_data.title,
            content=content,
        )

        return draft

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create resume draft.",
        )


# ============================================================
# GET ALL DRAFTS
# ============================================================

@router.get(
    "/drafts",
    response_model=list[ResumeDraftResponse],
)
def get_drafts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return get_resume_drafts_by_user(
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# GET ONE DRAFT
# ============================================================

@router.get(
    "/drafts/{draft_id}",
    response_model=ResumeDraftResponse,
)
def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    draft = get_resume_draft_by_id(
        db=db,
        draft_id=draft_id,
        user_id=current_user.id,
    )

    if draft is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume draft not found.",
        )

    return draft


# ============================================================
# UPDATE DRAFT
# ============================================================

@router.put(
    "/drafts/{draft_id}",
    response_model=ResumeDraftResponse,
)
def update_draft(
    draft_id: int,
    draft_data: ResumeDraftUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    draft = get_resume_draft_by_id(
        db=db,
        draft_id=draft_id,
        user_id=current_user.id,
    )

    if draft is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume draft not found.",
        )

    try:

        updated_draft = update_resume_draft(
            db=db,
            draft=draft,
            title=draft_data.title,
            content=draft_data.content,
        )

        return updated_draft

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update resume draft.",
        )


# ============================================================
# DELETE DRAFT
# ============================================================

@router.delete(
    "/drafts/{draft_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    draft = get_resume_draft_by_id(
        db=db,
        draft_id=draft_id,
        user_id=current_user.id,
    )

    if draft is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume draft not found.",
        )

    try:

        delete_resume_draft(
            db=db,
            draft=draft,
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume draft.",
        )


# ============================================================
# ATS VALIDATION
# ============================================================

@router.post(
    "/drafts/{draft_id}/validate",
    response_model=ATSValidationResponse,
)
def validate_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    draft = get_resume_draft_by_id(
        db=db,
        draft_id=draft_id,
        user_id=current_user.id,
    )

    if draft is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume draft not found.",
        )

    validation_result = validate_resume_for_ats(
        draft.content
    )

    return {
        "draft_id": draft.id,
        "is_valid": validation_result["is_valid"],
        "score": validation_result["score"],
        "issues": validation_result["issues"],
    }