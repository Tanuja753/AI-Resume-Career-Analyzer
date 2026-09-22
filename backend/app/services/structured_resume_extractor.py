import re

from app.schemas.structured_resume import (
    CertificationItem,
    EducationItem,
    ExperienceItem,
    PersonalInfo,
    ProjectItem,
    StructuredResume,
)


SECTION_ALIASES = {
    "education": {
        "education",
        "academic background",
        "academic qualifications",
        "qualifications",
    },
    "skills": {
        "skills",
        "technical skills",
        "technical skills and tools",
        "technologies",
        "technical expertise",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "internship",
        "internships",
    },
    "projects": {
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses and certifications",
    },
    "achievements": {
        "achievements",
        "awards",
        "honors",
        "accomplishments",
    },
}


def clean_line(line: str) -> str:
    line = line.strip()

    line = re.sub(
        r"^[•●▪◦■\-–—]+\s*",
        "",
        line,
    )

    return line.strip()


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


def detect_section_heading(line: str) -> str | None:
    normalized = normalize_heading(line)

    for section, aliases in SECTION_ALIASES.items():
        if normalized in aliases:
            return section

    return None

def extract_sections(text: str) -> dict[str, list[str]]:
    sections = {
        "education": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }

    current_section = None

    for raw_line in text.splitlines():
        line = clean_line(raw_line)

        if not line:
            continue

        detected_section = detect_section_heading(line)

        if detected_section:
            current_section = detected_section
            continue

        if current_section:
            sections[current_section].append(line)

    return sections

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)

    if match:
        return match.group(0)

    return None

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)


def extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)

    if match:
        return match.group(0)

    return None

def extract_name(text: str) -> str | None:
    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    for line in lines[:5]:
        if (
            "@" not in line
            and not re.search(r"\d", line)
            and len(line.split()) <= 5
        ):
            return line

    return None

def extract_location(text: str) -> str | None:
    location_patterns = [
        r"(?i)(?:location|address|city)\s*[:\-]\s*(.+)",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(1).strip()

    return None

def extract_skills(
    skill_lines: list[str],
) -> list[str]:

    skills = []

    for line in skill_lines:

        parts = re.split(
            r"[,|;/•]+",
            line,
        )

        for part in parts:

            skill = part.strip()

            if not skill:
                continue

            if len(skill) > 100:
                continue

            if skill not in skills:
                skills.append(skill)

    return skills

def extract_education(
    education_lines: list[str],
) -> list[EducationItem]:

    if not education_lines:
        return []

    education_items = []

    current_details = []

    for line in education_lines:

        year_match = re.search(
            r"\b(?:19|20)\d{2}(?:\s*[-–]\s*(?:19|20)\d{2})?\b",
            line,
        )

        if year_match:

            year = year_match.group(0)

            education_items.append(
                EducationItem(
                    degree=line,
                    year=year,
                )
            )

        else:

            current_details.append(line)

    if not education_items:

        education_items.append(
            EducationItem(
                details="\n".join(
                    education_lines
                )
            )
        )

    return education_items

def extract_experience(
    experience_lines: list[str],
) -> list[ExperienceItem]:

    if not experience_lines:
        return []

    items = []

    current_item = None

    for line in experience_lines:

        date_match = re.search(
            r"\b(?:19|20)\d{2}\s*[-–]\s*(?:19|20)?\d{2,4}\b"
            r"|\b(?:19|20)\d{2}\s*[-–]\s*(?:Present|present)\b",
            line,
        )

        if date_match:

            if current_item:
                items.append(current_item)

            current_item = ExperienceItem(
                duration=date_match.group(0),
                description=line,
            )

        elif current_item:

            if current_item.description:
                current_item.description += (
                    "\n" + line
                )
            else:
                current_item.description = line

        else:

            current_item = ExperienceItem(
                description=line
            )

    if current_item:
        items.append(current_item)

    return items

def extract_projects(
    project_lines: list[str],
) -> list[ProjectItem]:

    if not project_lines:
        return []

    projects = []

    current_project = None

    for line in project_lines:

        if current_project is None:

            current_project = ProjectItem(
                name=line
            )

        else:

            if current_project.description:
                current_project.description += (
                    "\n" + line
                )
            else:
                current_project.description = line

    if current_project:
        projects.append(current_project)

    return projects

def extract_certifications(
    certification_lines: list[str],
) -> list[CertificationItem]:

    certifications = []

    for line in certification_lines:

        year_match = re.search(
            r"\b(?:19|20)\d{2}\b",
            line,
        )

        year = (
            year_match.group(0)
            if year_match
            else None
        )

        certifications.append(
            CertificationItem(
                name=line,
                year=year,
            )
        )

    return certifications

def extract_achievements(
    achievement_lines: list[str],
) -> list[str]:

    return [
        line
        for line in achievement_lines
        if line
    ]

def extract_structured_resume(
    text: str,
) -> StructuredResume:

    if not text or not text.strip():
        raise ValueError(
            "Resume text is empty."
        )

    sections = extract_sections(text)

    personal_info = PersonalInfo(
        name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        location=extract_location(text),
    )

    education = extract_education(
        sections["education"]
    )

    skills = extract_skills(
        sections["skills"]
    )

    experience = extract_experience(
        sections["experience"]
    )

    projects = extract_projects(
        sections["projects"]
    )

    certifications = extract_certifications(
        sections["certifications"]
    )

    achievements = extract_achievements(
        sections["achievements"]
    )

    return StructuredResume(
        personal_info=personal_info,
        education=education,
        skills=skills,
        experience=experience,
        projects=projects,
        certifications=certifications,
        achievements=achievements,
    )

