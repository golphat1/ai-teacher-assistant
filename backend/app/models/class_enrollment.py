import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import EnrollmentStatus
from app.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.school_class import SchoolClass
    from app.models.user import User

class ClassEnrollment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "class_enrollments"
    __table_args__ =(UniqueConstraint("class_id", "student_id", name="uq_class_enrollments_class_student"),)
    
    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("class.id"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[EnrollmentStatus] = mapped_column(
        SAEnum(EnrollmentStatus, name="enrollment_status"), nullable=False, default=EnrollmentStatus.ACTIVE
    )
    
    school_class: Mapped["SchoolClass"] = relationship(back_populates="enrollments")
    student: Mapped["User"] = relationship()