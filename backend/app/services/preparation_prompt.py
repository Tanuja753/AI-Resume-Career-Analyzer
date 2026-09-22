import json


def build_preparation_prompt(
    *,
    target_job_title: str,
    structured_resume: dict,
    job_description: dict,
    matched_skills: list[str],
    partial_skills: list[str],
    missing_skills: list[str],
    interview_questions: list[dict],
) -> str:

    resume_json = json.dumps(
        structured_resume,
        indent=2,
        ensure_ascii=False,
    )

    job_json = json.dumps(
        job_description,
        indent=2,
        ensure_ascii=False,
    )

    questions_json = json.dumps(
        interview_questions,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are a personalized interview preparation plan generator.

Your task is to create a realistic preparation plan for a candidate
preparing for the target job.

TARGET JOB:
{target_job_title}

STRUCTURED RESUME:
{resume_json}

JOB DESCRIPTION:
{job_json}

MATCHED SKILLS:
{json.dumps(matched_skills)}

PARTIAL OR RELATED SKILLS:
{json.dumps(partial_skills)}

MISSING SKILLS:
{json.dumps(missing_skills)}

GENERATED INTERVIEW QUESTIONS:
{questions_json}

IMPORTANT RULES:

1. Prioritize missing skills first.
2. Use partial or related skills as secondary preparation areas.
3. Matched skills may be included when they are important for interview
   preparation.
4. Do not claim that the candidate knows a missing skill.
5. Do not invent qualifications, projects, employers, certifications,
   achievements, or experience.
6. The plan must be personalized to the target job.
7. Preparation activities should be practical and actionable.
8. Include topics that help answer the generated interview questions.
9. Keep estimated hours realistic.
10. Do not recommend preparation for technologies unrelated to the
    target job or identified skill gaps.
11. Return ONLY valid JSON.
12. Do not return markdown.
13. Do not return explanations outside JSON.

PRIORITY RULES:

- "high" = important missing skill or major interview gap
- "medium" = partial/related skill or important supporting topic
- "low" = matched skill that still needs interview practice

Each preparation item MUST contain:

- skill
- priority
- topic
- description
- action
- estimated_hours

The priority must be exactly one of:

"high"
"medium"
"low"

estimated_hours must be an integer between 1 and 40.

estimated_days must be an integer between 1 and 90.

Return JSON using exactly this structure:

{{
  "title": "Personalized Interview Preparation Plan",
  "summary": "Short summary of the preparation strategy.",
  "estimated_days": 14,
  "items": [
    {{
      "skill": "Docker",
      "priority": "high",
      "topic": "Docker fundamentals",
      "description": "Learn containers, images, Dockerfiles, and basic Docker commands.",
      "action": "Build and run a small FastAPI application using Docker.",
      "estimated_hours": 4
    }}
  ]
}}

IMPORTANT:

- Generate between 5 and 12 preparation items.
- Missing skills should receive high priority when relevant.
- Do not create duplicate preparation items.
- Every item must be relevant to the target job.
- Every item must contain all six required fields.
"""