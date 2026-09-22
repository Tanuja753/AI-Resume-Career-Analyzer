from pathlib import Path
from app.crud.resume import (
    create_resume,
    get_resume_by_id,
    update_resume_extraction,
    update_structured_resume,
)
from app.schemas.skill_match import (
    SkillMatchingResponse,
)

from app.services.skill_matching_service import (
    match_resume_with_job_description,
)
from app.crud.job_description import (
    get_job_description_by_id,
)

from app.schemas.structured_resume import (
    StructuredResumeResponse,
)

from app.services.structured_resume_extractor import (
    extract_structured_resume,
)

from app.schemas.skill import (
    ExtractedSkillsResponse,
)

from app.services.skill_processing_service import (
    extract_and_store_resume_skills,
)

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.file_validation import (
    validate_content_type,
    validate_file_extension,
    validate_file_size,
)
from app.crud.resume import (
    create_resume,
    get_resume_by_id,
    update_resume_extraction,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.resume import (
    ResumeExtractionResponse,
    ResumeResponse,
)
from app.services.resume_extractor import extract_resume_text

from uuid import uuid4


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    original_filename = file.filename

    if not original_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file has no filename.",
        )

    extension = validate_file_extension(
        original_filename
    )

    validate_content_type(
        file.content_type
    )

    file_size = await validate_file_size(file)

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        UPLOAD_DIR / stored_filename
    )

    try:

        with file_path.open("wb") as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception:

        if file_path.exists():
            file_path.unlink()

        raise

    try:

        resume = create_resume(
            db=db,
            user_id=current_user.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            content_type=file.content_type,
            file_size=file_size,
        )

    except Exception:

        if file_path.exists():
            file_path.unlink()

        raise

    return resume


@router.post(
    "/{resume_id}/extract",
    response_model=ResumeExtractionResponse,
)
def extract_resume(
    resume_id: int,
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

    file_path = Path(resume.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file could not be found.",
        )

    try:

        extracted_text = extract_resume_text(
            file_path=str(file_path),
            content_type=resume.content_type,
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to extract text from the resume.",
        )

    updated_resume = update_resume_extraction(
        db=db,
        resume=resume,
        extracted_text=extracted_text,
    )

    return updated_resume

@router.post(
    "/{resume_id}/structure",
    response_model=StructuredResumeResponse,
)
def structure_resume(
    resume_id: int,
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

    if not resume.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Resume text has not been extracted yet. "
                "Run text extraction first."
            ),
        )

    try:

        structured_resume = (
            extract_structured_resume(
                resume.extracted_text
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
                "Failed to structure resume information."
            ),
        )

    structured_data = (
        structured_resume.model_dump()
    )

    updated_resume = (
        update_structured_resume(
            db=db,
            resume=resume,
            structured_data=structured_data,
        )
    )

    return updated_resume

@router.post(
    "/{resume_id}/skills",
    response_model=ExtractedSkillsResponse,
)
def extract_resume_skills(
    resume_id: int,
    current_user: User = Depends(
        get_current_user
    ),
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

    try:

        skills = extract_and_store_resume_skills(
            db=db,
            resume=resume,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to extract resume skills.",
        )

    return {
        "source_id": resume.id,
        "source_type": "resume",
        "skills": skills,
    }

@router.post(
    "/{resume_id}/match/{job_description_id}",
    response_model=SkillMatchingResponse,
)
def match_resume_skills(
    resume_id: int,
    job_description_id: int,
    current_user: User = Depends(
        get_current_user
    ),
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

    job_description = (
        get_job_description_by_id(
            db=db,
            job_description_id=(
                job_description_id
            ),
            user_id=current_user.id,
        )
    )

    if job_description is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found.",
        )

    if not resume.resume_skills:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Resume skills have not been "
                "extracted yet."
            ),
        )

    if not job_description.job_description_skills:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Job description skills have not "
                "been extracted yet."
            ),
        )

    try:

        result = (
            match_resume_with_job_description(
                db=db,
                resume=resume,
                job_description=(
                    job_description
                ),
            )
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=422,
            detail=(
                "Failed to perform semantic "
                "skill matching."
            ),
        )

    return {
        "resume_id": resume.id,
        "job_description_id": (
            job_description.id
        ),
        "exact_matches": (
            result["exact_matches"]
        ),
        "semantic_matches": (
            result["semantic_matches"]
        ),
    }