from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PreparationProgress(Base):
    __tablename__ = "preparation_progress"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    plan_item_id: Mapped[int] = mapped_column(
        ForeignKey(
            "preparation_plan_items.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_started",
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    plan_item = relationship(
        "PreparationPlanItem",
    )