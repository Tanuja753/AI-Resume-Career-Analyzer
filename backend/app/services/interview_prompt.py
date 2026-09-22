import json


def build_interview_prompt(
    *,
    target_job_title: str,
    structured_resume: dict,
    job_description: dict,
    matched_skills: list[str],
    partial_skills: list[str],
    missing_skills: list[str],
    category: str,
    question_count: int,
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

    category_rules = {
        "technical": (
            "Generate technical questions about technologies, "
            "programming concepts, databases, APIs, backend development, "
            "and other technical requirements relevant to the target job."
        ),
        "resume_specific": (
            "Generate questions ONLY from facts explicitly present in "
            "the structured resume. Do not invent projects, technologies, "
            "experience, achievements, employers, certifications, or qualifications."
        ),
        "behavioral": (
            "Generate general behavioral interview questions relevant to "
            "the target job. Do not claim that the candidate has experienced "
            "a situation unless that experience is explicitly present in the resume."
        ),
        "scenario": (
            "Generate hypothetical job-related situations and ask how the "
            "candidate would handle them. Do not imply that the candidate "
            "has already experienced the situation."
        ),
    }

    category_instruction = category_rules[category]

    difficulty_instruction = """
Every question MUST contain a difficulty field.

The difficulty field is mandatory.

For example:

{
  "category": "behavioral",
  "question": "Describe a time when you solved a difficult problem.",
  "difficulty": "medium"
}

NEVER omit the difficulty field.
"""

    return f"""
You are an interview-question generation system.

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

CATEGORY:
{category}

{category_instruction}

Generate EXACTLY {question_count} questions.

IMPORTANT:
- Every generated question must have category "{category}".
- Generate exactly {question_count} questions.
- Do not generate fewer questions.
- Do not generate more questions.
- Every question MUST contain all three fields:
  "category"
  "question"
  "difficulty"
- The "difficulty" field is mandatory.
- NEVER omit the "difficulty" field.
- Difficulty must be exactly one of:
  "easy", "medium", "hard"
- Questions must be concise and interview-appropriate.
- Return ONLY valid JSON.
- Do not return markdown.
- Do not return explanations outside JSON.

{difficulty_instruction}

Required JSON structure:

{{
  "questions": [
    {{
      "category": "{category}",
      "question": "Question text",
      "difficulty": "medium"
    }},
    {{
      "category": "{category}",
      "question": "Another question text",
      "difficulty": "easy"
    }}
  ]
}}

MANDATORY:
Every object in the questions array MUST contain:
1. category
2. question
3. difficulty

The difficulty field MUST NOT be omitted.

The "questions" array MUST contain exactly {question_count} objects.
"""

