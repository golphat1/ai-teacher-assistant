import uuid
from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import QuestionType
from app.models.mixins import UUIDPrimaryKeyMixin


class Assessment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "assessments"
    lesson_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lesson_plans.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    questions: Mapped[list["AssessmentQuestion"]] = relationship(back_populates="assessment", cascade="all, delete-orphan")


class AssessmentQuestion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "assessment_questions"
    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False, index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(nullable=False)
    options: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    correct_answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=1.0)
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

    assessment: Mapped["Assessment"] = relationship(back_populates="questions")