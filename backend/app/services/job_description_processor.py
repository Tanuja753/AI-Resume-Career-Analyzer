import re

from app.schemas.job_description import (
    JobDescriptionStructured,
)


SECTION_ALIASES = {
    "responsibilities": {
        "responsibilities",
        "key responsibilities",
        "roles and responsibilities",
        "what you will do",
        "what you'll do",
        "duties",
    },
    "qualifications": {
        "qualifications",
        "requirements",
        "required qualifications",
        "basic qualifications",
        "preferred qualifications",
        "what we are looking for",
        "what we're looking for",
    },
    "other_requirements": {
        "preferred skills",
        "preferred requirements",
        "additional requirements",
        "nice to have",
        "preferred",
    },
}


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            line = re.sub(r"\s+", " ", line)
            lines.append(line)

    return "\n".join(lines)


def normalize_heading(text: str) -> str:
    text = text.strip().lower()

    text = re.sub(
        r"[:\-]+$",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def detect_section_heading(
    line: str,
) -> str | None:

    normalized = normalize_heading(line)

    for section, aliases in SECTION_ALIASES.items():

        if normalized in aliases:
            return section

    return None


def clean_bullet(line: str) -> str:
    return re.sub(
        r"^[•●▪◦■\-–—*]+\s*",
        "",
        line,
    ).strip()


def extract_sections(
    text: str,
) -> dict[str, list[str]]:

    sections = {
        "responsibilities": [],
        "qualifications": [],
        "other_requirements": [],
    }

    current_section = None

    for raw_line in text.splitlines():

        line = clean_bullet(raw_line)

        if not line:
            continue

        detected_section = detect_section_heading(line)

        if detected_section:
            current_section = detected_section
            continue

        if current_section:
            sections[current_section].append(line)

    return sections


def extract_company(
    text: str,
) -> str | None:

    patterns = [
        r"(?i)\bcompany\s*[:\-]\s*(.+)",
        r"(?i)\bemployer\s*[:\-]\s*(.+)",
        r"(?i)\borganization\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return None


def extract_location(
    text: str,
) -> str | None:

    patterns = [
        r"(?i)\blocation\s*[:\-]\s*(.+)",
        r"(?i)\bbased\s+in\s+(.+)",
        r"(?i)\bjob\s+location\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return None


def extract_employment_type(
    text: str,
) -> str | None:

    employment_types = [
        "full-time",
        "full time",
        "part-time",
        "part time",
        "internship",
        "contract",
        "temporary",
        "freelance",
        "hybrid",
        "remote",
    ]

    lowered_text = text.lower()

    found = []

    for employment_type in employment_types:

        if employment_type in lowered_text:
            found.append(employment_type)

    if not found:
        return None

    unique_types = list(dict.fromkeys(found))

    return ", ".join(unique_types)


def extract_experience_requirement(
    text: str,
) -> str | None:

    patterns = [
        r"(?i)\b\d+\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:relevant\s*)?(?:experience)?",
        r"(?i)\bexperience\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:

            value = match.group(0)

            return value.strip()

    return None


def extract_education_requirement(
    text: str,
) -> str | None:

    education_terms = [
        "bachelor",
        "bachelors",
        "b.tech",
        "b.e.",
        "engineering degree",
        "master",
        "masters",
        "m.tech",
        "m.e.",
        "degree",
        "computer science",
        "computer engineering",
    ]

    found = []

    lowered_text = text.lower()

    for term in education_terms:

        if term in lowered_text:
            found.append(term)

    if not found:
        return None

    return ", ".join(
        dict.fromkeys(found)
    )


def extract_job_title(
    target_job_title: str,
    text: str,
) -> str | None:

    if target_job_title.strip():
        return target_job_title.strip()

    patterns = [
        r"(?i)\bjob\s+title\s*[:\-]\s*(.+)",
        r"(?i)\bposition\s*[:\-]\s*(.+)",
        r"(?i)\brole\s*[:\-]\s*(.+)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return None


def extract_structured_job_description(
    target_job_title: str,
    text: str,
) -> tuple[str, JobDescriptionStructured]:

    if not text or not text.strip():
        raise ValueError(
            "Job description is empty."
        )

    cleaned_text = clean_text(text)

    sections = extract_sections(
        cleaned_text
    )

    structured = JobDescriptionStructured(
        job_title=extract_job_title(
            target_job_title,
            cleaned_text,
        ),
        company=extract_company(
            cleaned_text
        ),
        location=extract_location(
            cleaned_text
        ),
        employment_type=extract_employment_type(
            cleaned_text
        ),
        experience_required=extract_experience_requirement(
            cleaned_text
        ),
        education_required=extract_education_requirement(
            cleaned_text
        ),
        responsibilities=sections[
            "responsibilities"
        ],
        qualifications=sections[
            "qualifications"
        ],
        other_requirements=sections[
            "other_requirements"
        ],
    )

    return cleaned_text, structured