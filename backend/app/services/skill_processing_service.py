from sqlalchemy.orm import Session

from app.crud.job_description_skill import (
    create_job_description_skill,
    get_job_description_skill,
)

from app.crud.resume_skill import (
    create_resume_skill,
    get_resume_skill,
)

from app.crud.skill import (
    create_skill,
    get_skill_by_normalized_name,
)

from app.models.job_description import JobDescription
from app.models.resume import Resume

from app.services.skill_extractor import (
    extract_skills,
)


def get_or_create_skill(
    db: Session,
    skill_data: dict,
):

    skill = get_skill_by_normalized_name(
        db,
        skill_data["normalized_name"],
    )

    if skill:
        return skill

    return create_skill(
        db=db,
        name=skill_data["name"],
        normalized_name=skill_data[
            "normalized_name"
        ],
        category=skill_data["category"],
    )


def extract_and_store_resume_skills(
    db: Session,
    resume: Resume,
):

    if not resume.extracted_text:
        raise ValueError(
            "Resume text has not been extracted."
        )

    skills = extract_skills(
        resume.extracted_text
    )

    stored_skills = []

    for skill_data in skills:

        skill = get_or_create_skill(
            db,
            skill_data,
        )

        existing = get_resume_skill(
            db=db,
            resume_id=resume.id,
            skill_id=skill.id,
        )

        if not existing:

            create_resume_skill(
                db=db,
                resume_id=resume.id,
                skill_id=skill.id,
            )

        stored_skills.append(skill)

    db.commit()

    return stored_skills


def extract_and_store_job_description_skills(
    db: Session,
    job_description: JobDescription,
):

    if not job_description.raw_description:
        raise ValueError(
            "Job description is empty."
        )

    skills = extract_skills(
        job_description.raw_description
    )

    stored_skills = []

    for skill_data in skills:

        skill = get_or_create_skill(
            db,
            skill_data,
        )

        existing = get_job_description_skill(
            db=db,
            job_description_id=job_description.id,
            skill_id=skill.id,
        )

        if not existing:

            create_job_description_skill(
                db=db,
                job_description_id=job_description.id,
                skill_id=skill.id,
            )

        stored_skills.append(skill)

    db.commit()

    return stored_skills