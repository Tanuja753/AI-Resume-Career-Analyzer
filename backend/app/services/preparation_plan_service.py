import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.preparation_plan import (
    create_preparation_plan,
    create_preparation_plan_item,
    delete_preparation_plans,
)
from app.models.interview_question import InterviewQuestion
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.models.skill_gap import SkillGap
from app.schemas.preparation_plan import (
    GeneratedPreparationPlan,
)
from app.services.ollama_service import ollama_service
from app.services.preparation_prompt import (
    build_preparation_prompt,
)

MAX_ATTEMPTS = 2


def generate_preparation_plan(
    db: Session,
    *,
    resume: Resume,
    job_description: JobDescription,
):
    structured_resume = resume.structured_data or {}
    job_data = job_description.structured_data or {}

    # ---------------------------------------------------------
    # Get skill gap analysis
    # ---------------------------------------------------------

    skill_gap_statement = select(SkillGap).where(
        SkillGap.resume_id == resume.id,
        SkillGap.job_description_id == job_description.id,
    )

    skill_gaps = list(db.scalars(skill_gap_statement).all())

    if not skill_gaps:
        raise ValueError("Skill gap analysis has not been completed yet.")

    matched_skills = []
    partial_skills = []
    missing_skills = []

    for gap in skill_gaps:

        job_skill_name = gap.job_description_skill.skill.name

        if gap.gap_type == "matched":
            matched_skills.append(job_skill_name)

        elif gap.gap_type == "partial":
            partial_skills.append(job_skill_name)

        elif gap.gap_type == "missing":
            missing_skills.append(job_skill_name)

    # ---------------------------------------------------------
    # Get generated interview questions
    # ---------------------------------------------------------

    question_statement = (
        select(InterviewQuestion)
        .where(
            InterviewQuestion.resume_id == resume.id,
            InterviewQuestion.job_description_id == job_description.id,
        )
        .order_by(InterviewQuestion.id)
    )

    interview_questions = list(db.scalars(question_statement).all())

    if not interview_questions:
        raise ValueError("Interview questions have not been generated yet.")

    interview_question_data = [
        {
            "category": question.category,
            "question": question.question,
            "difficulty": question.difficulty,
        }
        for question in interview_questions
    ]

    # ---------------------------------------------------------
    # Build prompt
    # ---------------------------------------------------------

    prompt = build_preparation_prompt(
        target_job_title=job_description.target_job_title,
        structured_resume=structured_resume,
        job_description=job_data,
        matched_skills=matched_skills,
        partial_skills=partial_skills,
        missing_skills=missing_skills,
        interview_questions=interview_question_data,
    )

    # ---------------------------------------------------------
    # Generate with retry
    # ---------------------------------------------------------

    validated_plan = None
    last_error = None

    for attempt in range(
        1,
        MAX_ATTEMPTS + 1,
    ):

        current_prompt = prompt

        if attempt > 1:
            current_prompt += """

RETRY INSTRUCTION:

Your previous preparation plan response was invalid.

Generate the preparation plan again from scratch.

Before returning the response, verify that:

- The response is valid JSON.
- title is present.
- summary is present.
- estimated_days is present.
- items is present.
- Every item contains:
  skill
  priority
  topic
  description
  action
  estimated_hours
- priority is exactly:
  high, medium, or low
- estimated_hours is an integer from 1 to 40.
- estimated_days is an integer from 1 to 90.

Return ONLY the corrected JSON.
"""

        raw_response = ollama_service.generate(current_prompt)

        # -----------------------------------------------------
        # Validate JSON
        # -----------------------------------------------------

        try:
            parsed_response = json.loads(raw_response)

        except json.JSONDecodeError:

            last_error = "Ollama returned invalid JSON " "for the preparation plan."

            continue

        # -----------------------------------------------------
        # Validate Pydantic schema
        # -----------------------------------------------------

        try:
            validated_plan = GeneratedPreparationPlan.model_validate(parsed_response)

        except Exception as exc:

            last_error = f"Invalid preparation plan structure: {exc}"

            continue

        # -----------------------------------------------------
        # Additional validation
        # -----------------------------------------------------

        if not validated_plan.items:

            last_error = "Preparation plan contains no items."

            continue

        # -----------------------------------------------------
        # Successful validation
        # -----------------------------------------------------

        break

    # ---------------------------------------------------------
    # Failed after retries
    # ---------------------------------------------------------

    if validated_plan is None:

        raise ValueError(
            "Failed to generate a valid preparation plan "
            f"after {MAX_ATTEMPTS} attempts. "
            f"Last error: {last_error}"
        )

    # ---------------------------------------------------------
    # Delete previous plan
    # ---------------------------------------------------------

    delete_preparation_plans(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
    )

    db.flush()

    # ---------------------------------------------------------
    # Create new plan
    # ---------------------------------------------------------

    plan = create_preparation_plan(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
        title=validated_plan.title,
        summary=validated_plan.summary,
        estimated_days=validated_plan.estimated_days,
    )

    db.flush()

    # ---------------------------------------------------------
    # Create plan items
    # ---------------------------------------------------------

    generated_items = []

    try:

        for item_data in validated_plan.items:

            item = create_preparation_plan_item(
                db=db,
                plan_id=plan.id,
                skill=item_data.skill,
                priority=item_data.priority,
                topic=item_data.topic,
                description=item_data.description,
                action=item_data.action,
                estimated_hours=item_data.estimated_hours,
            )

            db.flush()

            generated_items.append(item)

        db.commit()

    except Exception:

        db.rollback()

        raise

    # ---------------------------------------------------------
    # Refresh objects
    # ---------------------------------------------------------

    db.refresh(plan)

    for item in generated_items:
        db.refresh(item)

    return plan
