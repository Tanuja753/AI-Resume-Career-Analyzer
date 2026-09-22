from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.preparation_progress import PreparationProgress


def get_progress_by_plan_item(
    db: Session,
    *,
    plan_item_id: int,
) -> PreparationProgress | None:
    statement = select(PreparationProgress).where(
        PreparationProgress.plan_item_id == plan_item_id
    )

    return db.scalars(statement).first()


def create_progress(
    db: Session,
    *,
    plan_item_id: int,
    status: str = "not_started",
    notes: str | None = None,
    completed_at: datetime | None = None,
) -> PreparationProgress:

    progress = PreparationProgress(
        plan_item_id=plan_item_id,
        status=status,
        notes=notes,
        completed_at=completed_at,
    )

    db.add(progress)

    return progress


def update_progress(
    db: Session,
    *,
    progress: PreparationProgress,
    status: str,
    notes: str | None,
    completed_at: datetime | None,
) -> PreparationProgress:

    progress.status = status
    progress.notes = notes
    progress.completed_at = completed_at

    db.add(progress)

    return progress