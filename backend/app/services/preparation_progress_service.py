from datetime import datetime
from app.core.datetime import utc_now
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.preparation_progress import (
    create_progress,
    get_progress_by_plan_item,
    update_progress,
)
from app.models.preparation_plan import (
    PreparationPlan,
    PreparationPlanItem,
)


def update_preparation_progress(
    db: Session,
    *,
    plan_item: PreparationPlanItem,
    status: str,
    notes: str | None,
):
    progress = get_progress_by_plan_item(
        db=db,
        plan_item_id=plan_item.id,
    )

    completed_at = None

    if status == "completed":
        if progress is not None and progress.completed_at is not None:
            completed_at = progress.completed_at
        else:
            completed_at = utc_now()

    if progress is None:
        progress = create_progress(
            db=db,
            plan_item_id=plan_item.id,
            status=status,
            notes=notes,
            completed_at=completed_at,
        )
    else:
        progress = update_progress(
            db=db,
            progress=progress,
            status=status,
            notes=notes,
            completed_at=completed_at,
        )

    db.commit()
    db.refresh(progress)

    return progress


def get_preparation_progress(
    db: Session,
    *,
    plan: PreparationPlan,
):
    statement = (
        select(PreparationPlanItem)
        .where(
            PreparationPlanItem.plan_id == plan.id
        )
        .order_by(PreparationPlanItem.id)
    )

    items = list(db.scalars(statement).all())

    total_items = len(items)
    not_started = 0
    in_progress = 0
    completed = 0

    response_items = []

    for item in items:

        progress = get_progress_by_plan_item(
            db=db,
            plan_item_id=item.id,
        )

        if progress is None:
            status = "not_started"
            notes = None
            completed_at = None

            not_started += 1

        else:
            status = progress.status
            notes = progress.notes
            completed_at = progress.completed_at

            if status == "not_started":
                not_started += 1

            elif status == "in_progress":
                in_progress += 1

            elif status == "completed":
                completed += 1

        response_items.append(
            {
                "plan_item_id": item.id,
                "skill": item.skill,
                "priority": item.priority,
                "topic": item.topic,
                "description": item.description,
                "action": item.action,
                "estimated_hours": item.estimated_hours,
                "status": status,
                "notes": notes,
                "completed_at": completed_at,
            }
        )

    if total_items == 0:
        progress_percentage = 0.0
    else:
        progress_percentage = round(
            (completed / total_items) * 100,
            2,
        )

    return {
        "resume_id": plan.resume_id,
        "job_description_id": plan.job_description_id,
        "plan_id": plan.id,
        "summary": {
            "total_items": total_items,
            "not_started": not_started,
            "in_progress": in_progress,
            "completed": completed,
            "progress_percentage": progress_percentage,
        },
        "items": response_items,
    }