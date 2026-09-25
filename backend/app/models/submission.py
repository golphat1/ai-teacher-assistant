import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import SubmissionStatus
from app.models.mixins import UUIDPrimaryKeyMixin


class StudentSubmission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "student_submissions"
    __table_args__ = (UniqueConstraint("assignment_id", "student_id", name="uq_submission_assignment_student"),)

    assignment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessment_assignments.id"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[SubmissionStatus] = mapped_column(nullable=False, default=SubmissionStatus.SUBMITTED)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    answers: Mapped[list["SubmissionAnswer"]] = relationship(back_populates="submission", cascade="all, delete-orphan")


class SubmissionAnswer(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "submission_answers"
    __table_args__ = (UniqueConstraint("submission_id", "question_id", name="uq_answer_submission_question"),)

    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student_submissions.id"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessment_questions.id"), nullable=False, index=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    submission: Mapped["StudentSubmission"] = relationship(back_populates="answers")