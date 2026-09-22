from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.skill_gap import (
    create_skill_gap,
    delete_skill_gaps,
)
from app.models.job_description import JobDescription
from app.models.skill_match import SkillMatch
from app.models.resume import Resume
from app.models.resume_skill import ResumeSkill


def analyze_skill_gaps(
    db: Session,
    resume: Resume,
    job_description: JobDescription,
):
    # Remove any previous skill-gap analysis
    # for this resume and job description.
    delete_skill_gaps(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
    )

    # Get Stage 11 skill-matching results.
    statement = select(SkillMatch).where(
        SkillMatch.resume_id == resume.id,
        SkillMatch.job_description_id == job_description.id,
    )

    matches = list(
        db.scalars(statement).all()
    )

    matched_skills = []
    missing_skills = []

    # Analyze every skill required by the job description.
    for jd_skill_relation in (
        job_description.job_description_skills
    ):
        jd_skill = jd_skill_relation.skill

        # Find the Stage 11 matching record
        # for the current job-description skill.
        matching_record = next(
            (
                match
                for match in matches
                if match.job_description_skill_id
                == jd_skill_relation.id
            ),
            None,
        )

        # ---------------------------------------------------------
        # MATCHED SKILL
        # ---------------------------------------------------------
        if matching_record:

            # Get the resume skill explicitly using the
            # resume_skill_id stored by Stage 11.
            resume_skill_name = None

            if matching_record.resume_skill_id is not None:

                resume_skill = db.get(
                    ResumeSkill,
                    matching_record.resume_skill_id,
                )

                if (
                    resume_skill is not None
                    and resume_skill.skill is not None
                ):
                    resume_skill_name = (
                        resume_skill.skill.name
                    )

            # Build transparent reasoning.
            reason = (
                f"Job requirement '{jd_skill.name}' "
                f"matched with resume skill "
                f"'{resume_skill_name}' using "
                f"{matching_record.matching_method}."
            )

            # Add similarity score when available.
            if matching_record.similarity_score is not None:
                reason += (
                    f" Similarity score: "
                    f"{matching_record.similarity_score:.4f}."
                )

            item = create_skill_gap(
                db=db,
                resume_id=resume.id,
                job_description_id=job_description.id,
                job_description_skill_id=jd_skill_relation.id,
                resume_skill_id=matching_record.resume_skill_id,
                gap_type="matched",
                similarity_score=matching_record.similarity_score,
                reason=reason,
            )

            # Flush so the database generates item.id
            # before we use it in the response.
            db.flush()

            matched_skills.append({
                "id": item.id,
                "job_skill": jd_skill.name,
                "resume_skill": resume_skill_name,
                "gap_type": "matched",
                "similarity_score": (
                    matching_record.similarity_score
                ),
                "reason": reason,
            })

        # ---------------------------------------------------------
        # MISSING SKILL
        # ---------------------------------------------------------
        else:

            reason = (
                f"Job requirement '{jd_skill.name}' "
                f"did not have a corresponding skill "
                f"identified in the resume."
            )

            item = create_skill_gap(
                db=db,
                resume_id=resume.id,
                job_description_id=job_description.id,
                job_description_skill_id=jd_skill_relation.id,
                resume_skill_id=None,
                gap_type="missing",
                similarity_score=None,
                reason=reason,
            )

            # Flush so the database generates item.id
            # before we use it in the response.
            db.flush()

            missing_skills.append({
                "id": item.id,
                "job_skill": jd_skill.name,
                "resume_skill": None,
                "gap_type": "missing",
                "similarity_score": None,
                "reason": reason,
            })

    # Permanently save the complete analysis.
    db.commit()

    return {
        "resume_id": resume.id,
        "job_description_id": job_description.id,
        "matched_skills": matched_skills,
        "partial_skills": [],
        "missing_skills": missing_skills,
        "summary": {
            "total_required": len(
                job_description.job_description_skills
            ),
            "matched": len(matched_skills),
            "partial": 0,
            "missing": len(missing_skills),
        },
    }