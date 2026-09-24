import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

# Same circular-import guard used in the other model files: User
# needs this module for type hints only, since User -> StudentProfile
# and StudentProfile -> User reference each other.
if TYPE_CHECKING:
    from app.models.user import User


class StudentProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """StudentProfile model holding student-specific data for a User.

    Exists as a separate table (rather than columns on User) because
    this data only applies to users with role="student" — keeping it
    separate avoids a `users` table full of nullable columns that only
    make sense for one role.
    """

    __tablename__ = "student_profiles"

    # One-to-one with User: unique=True ensures a user can have at
    # most one StudentProfile row.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )

    # Optional — schools may not collect this at signup, and some
    # student accounts (e.g. bulk-imported rosters) may fill it in later.
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Optional guardian contact for notifications/consent. Nullable
    # since not every student has a guardian email on file yet.
    guardian_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Back-reference to the owning User. Must match `back_populates`
    # exactly on User.student_profile for SQLAlchemy to pair the two.
    user: Mapped["User"] = relationship("User", back_populates="student_profile")