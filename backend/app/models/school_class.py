import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.class_enrollment import ClassEnrollment
    from app.models.user import User

class SchoolClass(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """

    Named SchoolClass not class to avoid colliding with python keyword class.
    """
    __tablename__ = "class"
    __table_args__ = (CheckConstraint("student_count >= 0", name="ck_classes_student_count_nonneg"),)

    school_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    teacher_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    student_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)

    teacher: Mapped["User"] = relationship()
    enrollments: Mapped[List["ClassEnrollment"]] = relationship(back_populates="school_class")