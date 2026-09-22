def build_initial_resume_content(
    structured_data: dict,
) -> dict:
    """
    Convert structured resume data into the editable
    resume-builder format.

    Only information already present in the structured
    resume is copied.
    """

    personal_info = structured_data.get(
        "personal_info",
        {},
    )

    education = structured_data.get(
        "education",
        [],
    )

    experience = structured_data.get(
        "experience",
        [],
    )

    projects = structured_data.get(
        "projects",
        [],
    )

    certifications = structured_data.get(
        "certifications",
        [],
    )

    skills = structured_data.get(
        "skills",
        [],
    )

    summary = structured_data.get(
        "summary",
        "",
    )

    return {
        "personal_info": {
            "name": personal_info.get(
                "name",
                "",
            ),
            "email": personal_info.get(
                "email",
                "",
            ),
            "phone": personal_info.get(
                "phone",
                "",
            ),
            "location": personal_info.get(
                "location",
                "",
            ),
            "linkedin": personal_info.get(
                "linkedin",
                "",
            ),
            "github": personal_info.get(
                "github",
                "",
            ),
        },

        "summary": summary,

        "skills": skills,

        "experience": experience,

        "projects": projects,

        "education": education,

        "certifications": certifications,
    }


def validate_resume_for_ats(
    content: dict,
) -> dict:

    issues = []

    personal_info = content.get(
        "personal_info",
        {},
    )

    summary = content.get(
        "summary",
        "",
    )

    skills = content.get(
        "skills",
        [],
    )

    experience = content.get(
        "experience",
        [],
    )

    projects = content.get(
        "projects",
        [],
    )

    education = content.get(
        "education",
        [],
    )

    certifications = content.get(
        "certifications",
        [],
    )

    # --------------------------------
    # Personal Information
    # --------------------------------

    if not personal_info.get("name"):

        issues.append(
            {
                "severity": "error",
                "section": "Personal Information",
                "message": "Name is missing.",
            }
        )

    if not personal_info.get("email"):

        issues.append(
            {
                "severity": "error",
                "section": "Personal Information",
                "message": "Email address is missing.",
            }
        )

    if not personal_info.get("phone"):

        issues.append(
            {
                "severity": "warning",
                "section": "Personal Information",
                "message": "Phone number is missing.",
            }
        )

    # --------------------------------
    # Summary
    # --------------------------------

    if not summary.strip():

        issues.append(
            {
                "severity": "warning",
                "section": "Summary",
                "message": "Professional summary is missing.",
            }
        )

    elif len(summary.split()) < 20:

        issues.append(
            {
                "severity": "warning",
                "section": "Summary",
                "message": "Professional summary is very short.",
            }
        )

    # --------------------------------
    # Skills
    # --------------------------------

    if not skills:

        issues.append(
            {
                "severity": "error",
                "section": "Skills",
                "message": "No skills have been added.",
            }
        )

    elif len(skills) < 5:

        issues.append(
            {
                "severity": "warning",
                "section": "Skills",
                "message": "Consider adding more relevant skills.",
            }
        )

    # --------------------------------
    # Education
    # --------------------------------

    if not education:

        issues.append(
            {
                "severity": "warning",
                "section": "Education",
                "message": "Education section is empty.",
            }
        )

    # --------------------------------
    # Experience / Projects
    # --------------------------------

    if not experience and not projects:

        issues.append(
            {
                "severity": "warning",
                "section": "Experience",
                "message": (
                    "No experience or projects are listed."
                ),
            }
        )

    # --------------------------------
    # Experience bullets
    # --------------------------------

    for index, item in enumerate(experience):

        bullets = item.get(
            "bullets",
            [],
        )

        for bullet in bullets:

            if len(bullet.split()) < 5:

                issues.append(
                    {
                        "severity": "warning",
                        "section": "Experience",
                        "message": (
                            f"Experience item {index + 1} "
                            "contains a very short bullet."
                        ),
                    }
                )

    # --------------------------------
    # Project bullets
    # --------------------------------

    for index, item in enumerate(projects):

        bullets = item.get(
            "bullets",
            [],
        )

        for bullet in bullets:

            if len(bullet.split()) < 5:

                issues.append(
                    {
                        "severity": "warning",
                        "section": "Projects",
                        "message": (
                            f"Project item {index + 1} "
                            "contains a very short bullet."
                        ),
                    }
                )

    # --------------------------------
    # Calculate transparent score
    # --------------------------------

    error_count = sum(
        1
        for issue in issues
        if issue["severity"] == "error"
    )

    warning_count = sum(
        1
        for issue in issues
        if issue["severity"] == "warning"
    )

    score = 100

    score -= error_count * 15
    score -= warning_count * 5

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    return {
        "is_valid": error_count == 0,
        "score": float(score),
        "issues": issues,
    }