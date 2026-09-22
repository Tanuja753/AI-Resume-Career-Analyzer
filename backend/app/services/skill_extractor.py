import re

from app.services.skill_dictionary import (
    SKILL_DICTIONARY,
)


def normalize_text(text: str) -> str:
    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def contains_skill(
    text: str,
    alias: str,
) -> bool:

    escaped_alias = re.escape(
        alias.lower()
    )

    pattern = (
        r"(?<![a-zA-Z0-9+#.])"
        + escaped_alias
        + r"(?![a-zA-Z0-9+#.])"
    )

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    ) is not None


def extract_skills(
    text: str,
) -> list[dict]:

    if not text or not text.strip():
        return []

    normalized_text = normalize_text(
        text
    )

    extracted_skills = []

    for skill_key, skill_info in (
        SKILL_DICTIONARY.items()
    ):

        for alias in skill_info["aliases"]:

            if contains_skill(
                normalized_text,
                alias,
            ):

                extracted_skills.append(
                    {
                        "name": skill_info["name"],
                        "normalized_name": skill_key,
                        "category": skill_info[
                            "category"
                        ],
                    }
                )

                break

    return extracted_skills