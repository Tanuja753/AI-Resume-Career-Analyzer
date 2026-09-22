from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.generated_resume import (
    create_generated_resume,
    get_generated_resume_by_id,
    get_generated_resumes_by_draft,
)
from app.crud.resume_draft import (
    get_resume_draft_by_id,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.generated_resume import (
    GeneratedResumeResponse,
)
from app.services.pdf_generator_service import (
    generate_resume_pdf,
)


router = APIRouter(
    prefix="/resume-pdf",
    tags=["Resume PDF"],
)


@router.post(
    "/drafts/{draft_id}/generate",
    response_model=GeneratedResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_pdf(
    draft_id: int,
    current_user: User = Depends(
        get_current_user
    ),
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

    unique_id = uuid4().hex

    file_name = (
        f"resume_{draft.id}_{unique_id}.pdf"
    )

    try:

        output_path = generate_resume_pdf(
            content=draft.content,
            output_filename=file_name,
        )

        generated_resume = create_generated_resume(
            db=db,
            user_id=current_user.id,
            draft_id=draft.id,
            file_name=file_name,
            file_path=str(output_path),
        )

        return generated_resume

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate resume PDF.",
        )


@router.get(
    "/drafts/{draft_id}",
    response_model=list[GeneratedResumeResponse],
)
def get_generated_pdfs(
    draft_id: int,
    current_user: User = Depends(
        get_current_user
    ),
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

    return get_generated_resumes_by_draft(
        db=db,
        draft_id=draft.id,
        user_id=current_user.id,
    )


@router.get(
    "/{generated_resume_id}/download",
)
def download_pdf(
    generated_resume_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    generated_resume = get_generated_resume_by_id(
        db=db,
        generated_resume_id=generated_resume_id,
        user_id=current_user.id,
    )

    if generated_resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated resume not found.",
        )

    file_path = Path(
        generated_resume.file_path
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file does not exist.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=generated_resume.file_name,
    )