import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class LessonContent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "lesson_contents"

    # Foreign key to the parent plan; unique=True makes this one-to-one
    lesson_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lesson_plans.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # AI-generated sections stored as JSON
    learning_objective: Mapped[list] = mapped_column(JSONB, nullable=False)
    teaching_activity: Mapped[list] = mapped_column(JSONB, nullable=False)
    differentiated_activities: Mapped[list] = mapped_column(JSONB, nullable=False)
    assessment_questions: Mapped[list] = mapped_column(JSONB, nullable=False)
    marking_rubric: Mapped[list] = mapped_column(JSONB, nullable=False)
    homework: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    revision_questions: Mapped[list] = mapped_column(JSONB, nullable=False)

    # Generation metadata
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ai_provider_used: Mapped[str] = mapped_column(String(50), nullable=False)
    ai_model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    lesson_plan: Mapped["LessonPlan"] = relationship(back_populates="content")