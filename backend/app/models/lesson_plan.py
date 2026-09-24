import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import LessonStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.lesson_content import LessonContent

class LessonPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "lesson_plans"
    __table_args__ = (
        CheckConstraint("student_count > 0", name="ck_lesson_plans_student_count_positive"),
        CheckConstraint("duration_minutes > 0", name="ck_lesson_plans_duration_positive"),
    )
    
    school_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True
    )
    
    teacher_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    class_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("class.id"), nullable=False, index=True
    )
    
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    student_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    curriculum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ability_level: Mapped[str] = mapped_column(String(50), nullable=False)
    learning_context: Mapped[str | None] = mapped_column(String(100), nullable=True)
    additional_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    status: Mapped[LessonStatus] = mapped_column(
        SAEnum(LessonStatus, name="lesson_status"), nullable=False, default=LessonStatus.DRAFT
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    content: Mapped["LessonContent | None"] = relationship(
        back_populates="lesson_plan", uselist=False, cascade="all, delete-orphan"
    )