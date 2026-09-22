from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PreparationPlan(Base):
    __tablename__ = "preparation_plans"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    estimated_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    resume = relationship("Resume")

    job_description = relationship("JobDescription")

    items = relationship(
        "PreparationPlanItem",
        back_populates="plan",
        cascade="all, delete-orphan",
    )

    


class PreparationPlanItem(Base):
    __tablename__ = "preparation_plan_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("preparation_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    estimated_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    plan = relationship(
        "PreparationPlan",
        back_populates="items",
    )

    progress = relationship(
            "PreparationProgress",
            back_populates="plan_item",
            uselist=False,
            cascade="all, delete-orphan",
    )