from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skill import Skill


def get_skill_by_normalized_name(
    db: Session,
    normalized_name: str,
) -> Skill | None:

    statement = (
        select(Skill)
        .where(
            Skill.normalized_name
            == normalized_name
        )
    )

    return db.scalar(statement)


def create_skill(
    db: Session,
    name: str,
    normalized_name: str,
    category: str,
) -> Skill:

    skill = Skill(
        name=name,
        normalized_name=normalized_name,
        category=category,
    )

    db.add(skill)
    db.flush()

    return skill