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

from app.crud.resume import (
    get_resume_by_id,
)

from app.database.database import get_db

from app.models.user import User
from app.models.skill_gap import SkillGap

from app.schemas.skill_gap import (
    SkillGapAnalysisResponse,
)

from app.services.skill_gap_service import (
    analyze_skill_gaps,
)


router = APIRouter(
    prefix="/skill-gaps",
    tags=["Skill Gap Analysis"],
)


# ============================================================
# POST - ANALYZE SKILL GAPS
# ============================================================

@router.post(
    "/resume/{resume_id}/job-description/"
    "{job_description_id}",
    response_model=SkillGapAnalysisResponse,
)
def analyze_resume_skill_gaps(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

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

    if not resume.resume_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume skills have not been "
                "extracted yet"
            ),
        )

    if not job_description.job_description_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Job description skills have not "
                "been extracted yet"
            ),
        )

    try:

        result = analyze_skill_gaps(
            db=db,
            resume=resume,
            job_description=job_description,
        )

        return result

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to analyze skill gaps"
            ),
        )


# ============================================================
# GET - GET EXISTING SKILL GAP ANALYSIS
# ============================================================

@router.get(
    "/resume/{resume_id}/job-description/"
    "{job_description_id}",
    response_model=SkillGapAnalysisResponse,
)
def get_resume_skill_gaps(
    resume_id: int,
    job_description_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Verify resume belongs to current user
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Verify job description belongs to current user
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Get saved skill-gap records
    # --------------------------------------------------------

    skill_gaps = (
        db.query(SkillGap)
        .filter(
            SkillGap.resume_id == resume_id,
            SkillGap.job_description_id
            == job_description_id,
        )
        .all()
    )

    if not skill_gaps:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill gap analysis not found",
        )

    matched_skills = []
    partial_skills = []
    missing_skills = []

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    for gap in skill_gaps:

        # Get required/job skill name
        skill_name = (
            gap.job_description_skill.skill.name
            if gap.job_description_skill
            and gap.job_description_skill.skill
            else "Unknown"
        )

        # Get resume skill name
        resume_skill_name = None

        if gap.resume_skill is not None:
            if gap.resume_skill.skill is not None:
                resume_skill_name = (
                    gap.resume_skill.skill.name
                )

        # Build complete skill item
        skill_item = {
            "id": gap.id,

            "job_skill": skill_name,

            "resume_skill": resume_skill_name,

            "gap_type": gap.gap_type,

            "similarity_score": (
                gap.similarity_score
            ),

            "reason": gap.reason,
        }

        # Categorize the skill
        if gap.gap_type == "matched":

            matched_skills.append(
                skill_item
            )

        elif gap.gap_type == "partial":

            partial_skills.append(
                skill_item
            )

        elif gap.gap_type == "missing":

            missing_skills.append(
                skill_item
            )

    # --------------------------------------------------------
    # Calculate summary
    # --------------------------------------------------------

    total_required = len(skill_gaps)

    matched = len(matched_skills)

    partial = len(partial_skills)

    missing = len(missing_skills)

    # --------------------------------------------------------
    # Return complete response
    # --------------------------------------------------------

    return {
        "resume_id": resume_id,

        "job_description_id": job_description_id,

        "matched_skills": matched_skills,

        "partial_skills": partial_skills,

        "missing_skills": missing_skills,

        "summary": {
            "total_required": total_required,
            "matched": matched,
            "partial": partial,
            "missing": missing,
        },
    }