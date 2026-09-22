from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.job_compatibility import (
    create_job_compatibility,
    get_job_compatibility,
)
from app.models.job_description import JobDescription
from app.models.skill_gap import SkillGap
from app.models.resume import Resume


def analyze_job_compatibility(
    db: Session,
    resume: Resume,
    job_description: JobDescription,
):
    # ---------------------------------------------------------
    # GET STAGE 12 SKILL-GAP RESULTS
    # ---------------------------------------------------------

    statement = select(SkillGap).where(
        SkillGap.resume_id == resume.id,
        SkillGap.job_description_id == job_description.id,
    )

    skill_gaps = list(
        db.scalars(statement).all()
    )

    if not skill_gaps:
        raise ValueError(
            "Skill gap analysis has not been completed yet."
        )

    # ---------------------------------------------------------
    # COUNT GAP TYPES
    # ---------------------------------------------------------

    matched = sum(
        1
        for gap in skill_gaps
        if gap.gap_type == "matched"
    )

    partial = sum(
        1
        for gap in skill_gaps
        if gap.gap_type == "partial"
    )

    missing = sum(
        1
        for gap in skill_gaps
        if gap.gap_type == "missing"
    )

    total_required = len(skill_gaps)

    # ---------------------------------------------------------
    # SKILL COVERAGE
    # ---------------------------------------------------------

    if total_required == 0:
        skill_coverage_percentage = 0.0

    else:
        weighted_matched = (
            matched + (0.5 * partial)
        )

        skill_coverage_percentage = (
            weighted_matched
            / total_required
            * 100
        )

    # ---------------------------------------------------------
    # SEMANTIC MATCH QUALITY
    # ---------------------------------------------------------

    total_similarity = sum(
        gap.similarity_score or 0.0
        for gap in skill_gaps
    )

    if total_required == 0:
        semantic_match_percentage = 0.0

    else:
        semantic_match_percentage = (
            total_similarity
            / total_required
            * 100
        )

    # ---------------------------------------------------------
    # COMPATIBILITY SCORE
    # ---------------------------------------------------------

    compatibility_score = (
        (0.70 * skill_coverage_percentage)
        + (0.30 * semantic_match_percentage)
    )

    # Keep floating-point values within 0-100.
    compatibility_score = max(
        0.0,
        min(100.0, compatibility_score),
    )

    skill_coverage_percentage = max(
        0.0,
        min(100.0, skill_coverage_percentage),
    )

    semantic_match_percentage = max(
        0.0,
        min(100.0, semantic_match_percentage),
    )

    # ---------------------------------------------------------
    # TRANSPARENT EXPLANATION
    # ---------------------------------------------------------

    explanation = (
        f"The compatibility analysis is based on "
        f"{total_required} required skills identified "
        f"in the job description. "
        f"{matched} skills were matched, "
        f"{partial} were identified as partial or related, "
        f"and {missing} were not identified in the resume. "
        f"Skill coverage is calculated by giving full weight "
        f"to matched skills and half weight to partial skills. "
        f"Semantic match quality is calculated from the "
        f"similarity scores stored during skill matching. "
        f"The final compatibility score combines "
        f"70% skill coverage and 30% semantic match quality."
    )

    # ---------------------------------------------------------
    # CHECK EXISTING RESULT
    # ---------------------------------------------------------

    compatibility = get_job_compatibility(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
    )

    # ---------------------------------------------------------
    # UPDATE EXISTING RESULT
    # ---------------------------------------------------------

    if compatibility:

        compatibility.total_required = total_required
        compatibility.matched = matched
        compatibility.partial = partial
        compatibility.missing = missing

        compatibility.skill_coverage_percentage = (
            skill_coverage_percentage
        )

        compatibility.semantic_match_percentage = (
            semantic_match_percentage
        )

        compatibility.compatibility_score = (
            compatibility_score
        )

        compatibility.explanation = explanation

        db.commit()
        db.refresh(compatibility)

        return compatibility

    # ---------------------------------------------------------
    # CREATE NEW RESULT
    # ---------------------------------------------------------

    compatibility = create_job_compatibility(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
        total_required=total_required,
        matched=matched,
        partial=partial,
        missing=missing,
        skill_coverage_percentage=skill_coverage_percentage,
        semantic_match_percentage=semantic_match_percentage,
        compatibility_score=compatibility_score,
        explanation=explanation,
    )

    db.flush()

    db.commit()

    db.refresh(compatibility)

    return compatibility