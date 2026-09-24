import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

# Type-checking-only import, same pattern as every other model file:
# User -> TeacherProfile and TeacherProfile -> User reference each
# other, so importing User directly here at runtime would create a
# circular import.
if TYPE_CHECKING:
    from app.models.user import User


class TeacherProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """TeacherProfile model holding teacher-specific data for a User.

    Kept as a separate table from User for the same reason as
    StudentProfile: this data only applies to role="teacher" accounts.
    """

    __tablename__ = "teacher_profiles"

    # One-to-one with User: unique=True ensures a user can have at
    # most one TeacherProfile row.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )

    # Optional — not every school tracks department at the profile
    # level, and it can be filled in after initial account creation.
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # SmallInteger is enough range for a career-length number of years
    # and is cheaper than a full Integer column at scale.
    years_experience: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    # Back-reference to the owning User. Must match `back_populates`
    # exactly on User.teacher_profile for SQLAlchemy to pair the two.
    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")