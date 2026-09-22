from sqlalchemy.orm import Session

from app.core.config import (
    SEMANTIC_MATCH_THRESHOLD,
)

from app.crud.skill_match import (
    create_skill_match,
    delete_skill_matches,
)

from app.models.job_description import (
    JobDescription,
)

from app.models.resume import Resume

from app.models.resume_skill import (
    ResumeSkill,
)

from app.models.job_description_skill import (
    JobDescriptionSkill,
)

from app.services.semantic_matcher import (
    semantic_skill_matcher,
)


def match_resume_with_job_description(
    db: Session,
    resume: Resume,
    job_description: JobDescription,
):
    resume_skills = list(
        resume.resume_skills
    )

    job_skills = list(
        job_description.job_description_skills
    )

    delete_skill_matches(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
    )

    exact_matches = []
    semantic_matches = []

    matched_resume_skill_ids = set()

    # ------------------------------------------------
    # STEP 1: EXACT MATCHING
    # ------------------------------------------------

    for job_skill_relation in job_skills:

        job_skill = (
            job_skill_relation.skill
        )

        for resume_skill_relation in (
            resume_skills
        ):

            resume_skill = (
                resume_skill_relation.skill
            )

            if (
                job_skill.normalized_name
                == resume_skill.normalized_name
            ):

                create_skill_match(
                    db=db,
                    resume_id=resume.id,
                    job_description_id=(
                        job_description.id
                    ),
                    resume_skill_id=(
                        resume_skill_relation.id
                    ),
                    job_description_skill_id=(
                        job_skill_relation.id
                    ),
                    match_type="exact",
                    similarity_score=1.0,
                    matching_method=(
                        "normalized_name"
                    ),
                )

                exact_matches.append(
                    {
                        "job_skill": (
                            job_skill.name
                        ),
                        "resume_skill": (
                            resume_skill.name
                        ),
                        "match_type": "exact",
                        "similarity_score": 1.0,
                        "matching_method": (
                            "normalized_name"
                        ),
                    }
                )

                matched_resume_skill_ids.add(
                    resume_skill_relation.id
                )

                break

    # ------------------------------------------------
    # STEP 2: SEMANTIC MATCHING
    # ------------------------------------------------

    unmatched_job_skills = [
        relation
        for relation in job_skills
        if not any(
            match["job_skill"]
            == relation.skill.name
            for match in exact_matches
        )
    ]

    unmatched_resume_skills = [
        relation
        for relation in resume_skills
        if relation.id
        not in matched_resume_skill_ids
    ]

    for job_skill_relation in (
        unmatched_job_skills
    ):

        job_skill = (
            job_skill_relation.skill
        )

        best_resume_skill = None
        best_score = None

        for resume_skill_relation in (
            unmatched_resume_skills
        ):

            resume_skill = (
                resume_skill_relation.skill
            )

            # ----------------------------------------
            # Category guard
            # ----------------------------------------

            if (
                job_skill.category
                != resume_skill.category
            ):
                continue

            score = (
                semantic_skill_matcher
                .calculate_similarity(
                    job_skill.name,
                    resume_skill.name,
                )
            )

            if (
                best_score is None
                or score > best_score
            ):

                best_score = score
                best_resume_skill = (
                    resume_skill_relation
                )

        if (
            best_resume_skill is not None
            and best_score is not None
            and best_score
            >= SEMANTIC_MATCH_THRESHOLD
        ):

            resume_skill = (
                best_resume_skill.skill
            )

            create_skill_match(
                db=db,
                resume_id=resume.id,
                job_description_id=(
                    job_description.id
                ),
                resume_skill_id=(
                    best_resume_skill.id
                ),
                job_description_skill_id=(
                    job_skill_relation.id
                ),
                match_type="semantic",
                similarity_score=round(
                    best_score,
                    4,
                ),
                matching_method=(
                    "sentence_transformer"
                ),
            )

            semantic_matches.append(
                {
                    "job_skill": (
                        job_skill.name
                    ),
                    "resume_skill": (
                        resume_skill.name
                    ),
                    "match_type": "semantic",
                    "similarity_score": round(
                        best_score,
                        4,
                    ),
                    "matching_method": (
                        "sentence_transformer"
                    ),
                }
            )

            unmatched_resume_skills = [
                relation
                for relation in (
                    unmatched_resume_skills
                )
                if relation.id
                != best_resume_skill.id
            ]

    db.commit()

    return {
        "exact_matches": exact_matches,
        "semantic_matches": semantic_matches,
    }