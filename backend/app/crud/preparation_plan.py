from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.preparation_plan import (
    PreparationPlan,
    PreparationPlanItem,
)


def delete_preparation_plans(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
) -> None:

    statement = delete(PreparationPlan).where(
        PreparationPlan.resume_id == resume_id,
        PreparationPlan.job_description_id == job_description_id,
    )

    db.execute(statement)


def create_preparation_plan(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
    title: str,
    summary: str,
    estimated_days: int,
) -> PreparationPlan:

    plan = PreparationPlan(
        resume_id=resume_id,
        job_description_id=job_description_id,
        title=title,
        summary=summary,
        estimated_days=estimated_days,
    )

    db.add(plan)

    return plan


def create_preparation_plan_item(
    db: Session,
    *,
    plan_id: int,
    skill: str,
    priority: str,
    topic: str,
    description: str,
    action: str,
    estimated_hours: int,
) -> PreparationPlanItem:

    item = PreparationPlanItem(
        plan_id=plan_id,
        skill=skill,
        priority=priority,
        topic=topic,
        description=description,
        action=action,
        estimated_hours=estimated_hours,
    )

    db.add(item)

    return item


def get_preparation_plan(
    db: Session,
    *,
    resume_id: int,
    job_description_id: int,
) -> PreparationPlan | None:

    statement = select(PreparationPlan).where(
        PreparationPlan.resume_id == resume_id,
        PreparationPlan.job_description_id == job_description_id,
    )

    return db.scalars(statement).first()

def get_preparation_plan_item(
    db: Session,
    *,
    plan_item_id: int,
) -> PreparationPlanItem | None:

    statement = select(PreparationPlanItem).where(
        PreparationPlanItem.id == plan_item_id
    )

    return db.scalars(statement).first()