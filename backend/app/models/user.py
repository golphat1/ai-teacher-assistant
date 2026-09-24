import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

# Type-checking-only imports to avoid circular imports: School,
# TeacherProfile, StudentProfile, and RefreshToken all import User
# back (directly or via relationship), so importing them for real at
# module load time here would create an import loop. The string
# arguments passed to relationship() below are what actually let
# SQLAlchemy resolve these classes later, once every model is loaded.
if TYPE_CHECKING:
    from app.models.school import School
    from app.models.teacher_profile import TeacherProfile
    from app.models.student_profile import StudentProfile
    from app.models.refresh_token import RefreshToken


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """User model representing a single account: teacher, student, or admin.

    A user optionally belongs to a School (nullable only for
    `super_admin`, enforced by the check constraint below), and has at
    most one of a TeacherProfile or StudentProfile depending on `role`.
    """

    __tablename__ = "users"
    __table_args__ = (
        # One email per school, not globally unique — the same person's
        # email could plausibly appear at two different schools.
        UniqueConstraint("school_id", "email", name="uq_users_school_email"),
        # Every user must belong to a school UNLESS they're a super_admin,
        # who operates above the school level and isn't tenant-scoped.
        CheckConstraint(
            "role = 'super_admin' OR school_id IS NOT NULL",
            name="ck_users_school_required_unless_super_admin",
        ),
    )

    school_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    #role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), nullable=False)
    
    role: Mapped[UserRole] = mapped_column(
    SAEnum(
        UserRole,
        name="user_role",
        # Without this, SQLAlchemy uses each member's .name (e.g.
        # "SUPER_ADMIN") to populate the Postgres enum type, instead
        # of .value (e.g. "super_admin"). Since the CHECK constraint
        # below compares role against the lowercase string, the two
        # must match exactly.
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    nullable=False,
)

    # Many-to-one back to School. Nullable to match `school_id`, for
    # the super_admin case where there's no school at all.
    school: Mapped["School | None"] = relationship("School", back_populates="users")

    # One-to-one profiles. `uselist=False` tells SQLAlchemy this is a
    # single object, not a list, even though relationship() defaults
    # to list-returning for one-to-many. `cascade="all, delete-orphan"`
    # means deleting a User deletes their profile row too, and a
    # profile row can't exist detached from its user.
    teacher_profile: Mapped["TeacherProfile | None"] = relationship(
        "TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    student_profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # One-to-many back to RefreshToken, matching the `back_populates="user"`
    # set on RefreshToken.user. Without this side existing (and named
    # exactly "refresh_tokens"), RefreshToken's relationship would fail
    # to configure — the two back_populates names must reference each other.
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )