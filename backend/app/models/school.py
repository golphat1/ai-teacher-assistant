from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin

# Only import User for type-checking purposes, not at runtime.
# This avoids a circular import: User probably imports School back
# (or will, once its `school` relationship is added), and if both
# files import each other directly at module load time, Python
# raises an ImportError. Since `relationship("User", ...)` below
# already uses a string reference, SQLAlchemy resolves the real
# class lazily — we don't need the live import at runtime, only
# for static type checkers like mypy/Pylance.
if TYPE_CHECKING:
    from app.models.user import User


class School(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """School model representing a school entity (tenant) in the system.

    Every user, class, and enrollment belongs to exactly one School,
    which is the unit of multi-tenant isolation across the app.
    """

    __tablename__ = "schools"

    # Human-readable school name. Required and unique so two schools
    # can't collide under the same display name.
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Optional email/organization domain (e.g. "lincolnhigh.edu"), used
    # for domain-based auto-enrollment or SSO in the future. Unique so
    # one domain can't be claimed by two schools, but nullable since
    # not every school will set one up right away.
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)

    # Which subscription plan this school is on. Defaults to "free"
    # so new schools aren't blocked on payment setup during onboarding.
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="free")

    # One-to-many: a School has many Users (teachers/students/admins).
    # The string "User" (not the imported class) is what lets this line
    # work even though User isn't imported at runtime — SQLAlchemy
    # resolves the string against its mapper registry once all models
    # have loaded, regardless of import order.
    users: Mapped[list["User"]] = relationship("User", back_populates="school")
    
    grade_release_policy: Mapped[str] = mapped_column(String(30), nullable=False, default="requires_teacher_review")
    # values: "auto_release" | "requires_teacher_review"