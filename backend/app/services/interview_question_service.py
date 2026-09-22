import json

from sqlalchemy.orm import Session

from app.crud.interview_question import (
    create_interview_question,
    delete_interview_questions,
)
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.interview_question import (
    GeneratedInterviewQuestions,
)
from app.services.interview_prompt import (
    build_interview_prompt,
)
from app.services.ollama_service import (
    ollama_service,
)

CATEGORY_COUNTS = {
    "technical": 4,
    "resume_specific": 3,
    "behavioral": 2,
    "scenario": 3,
}

MAX_ATTEMPTS_PER_CATEGORY = 2


def generate_interview_questions(
    db: Session,
    *,
    resume: Resume,
    job_description: JobDescription,
    matched_skills: list[str],
    partial_skills: list[str],
    missing_skills: list[str],
):
    structured_resume = resume.structured_data or {}
    job_data = job_description.structured_data or {}

    all_questions = []

    for category, question_count in CATEGORY_COUNTS.items():

        validated_questions = None
        last_error = None

        for attempt in range(1, MAX_ATTEMPTS_PER_CATEGORY + 1):

            prompt = build_interview_prompt(
                target_job_title=job_description.target_job_title,
                structured_resume=structured_resume,
                job_description=job_data,
                matched_skills=matched_skills,
                partial_skills=partial_skills,
                missing_skills=missing_skills,
                category=category,
                question_count=question_count,
            )

            # If this is a retry, explicitly tell the model
            # that the previous response was invalid.
            if attempt > 1:
                prompt += """

RETRY INSTRUCTION:

Your previous response for this category was invalid.

Generate the questions again from scratch.

Before returning the response, verify that EVERY question object
contains ALL THREE fields:

1. category
2. question
3. difficulty

The difficulty field is mandatory.

Do not omit difficulty from ANY question.

Return ONLY the corrected JSON object.
"""

            raw_response = ollama_service.generate(prompt)

            # -------------------------------------------------
            # Step 1: Validate JSON
            # -------------------------------------------------
            try:
                parsed_response = json.loads(raw_response)
            except json.JSONDecodeError:
                last_error = (
                    f"Ollama returned invalid JSON for " f"{category} questions."
                )

                continue

            # -------------------------------------------------
            # Step 2: Validate structure using Pydantic
            # -------------------------------------------------
            try:
                validated = GeneratedInterviewQuestions.model_validate(parsed_response)
            except Exception as exc:
                last_error = f"Invalid question structure for " f"{category}: {exc}"

                continue

            # -------------------------------------------------
            # Step 3: Validate exact question count
            # -------------------------------------------------
            if len(validated.questions) != question_count:

                last_error = (
                    f"Ollama generated "
                    f"{len(validated.questions)} "
                    f"{category} questions. "
                    f"Expected {question_count}."
                )

                continue

            # -------------------------------------------------
            # Step 4: Validate category
            # -------------------------------------------------
            category_is_valid = True

            for question in validated.questions:

                if question.category != category:

                    last_error = (
                        f"Ollama returned incorrect category "
                        f"'{question.category}' for a "
                        f"'{category}' question."
                    )

                    category_is_valid = False
                    break

            if not category_is_valid:
                continue

            # -------------------------------------------------
            # All validation checks passed
            # -------------------------------------------------
            validated_questions = validated.questions

            break

        # -----------------------------------------------------
        # Category failed after all retry attempts
        # -----------------------------------------------------
        if validated_questions is None:

            raise ValueError(
                f"Failed to generate valid {category} "
                f"questions after "
                f"{MAX_ATTEMPTS_PER_CATEGORY} attempts. "
                f"Last error: {last_error}"
            )

        all_questions.extend(validated_questions)

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------
    if len(all_questions) != 12:
        raise ValueError(
            "Interview question generation did not produce "
            "exactly 12 valid questions."
        )

    # ---------------------------------------------------------
    # Delete old questions ONLY after all new questions
    # have successfully passed validation.
    # ---------------------------------------------------------
    delete_interview_questions(
        db=db,
        resume_id=resume.id,
        job_description_id=job_description.id,
    )

    generated_questions = []

    # ---------------------------------------------------------
    # Save validated questions to database
    # ---------------------------------------------------------
    try:

        for question_data in all_questions:

            item = create_interview_question(
                db=db,
                resume_id=resume.id,
                job_description_id=job_description.id,
                category=question_data.category,
                question=question_data.question,
                difficulty=question_data.difficulty,
                source="ollama",
            )

            db.flush()

            generated_questions.append(item)

        db.commit()

    except Exception:
        db.rollback()
        raise

    # ---------------------------------------------------------
    # Refresh saved objects
    # ---------------------------------------------------------
    for item in generated_questions:
        db.refresh(item)

    return generated_questions
