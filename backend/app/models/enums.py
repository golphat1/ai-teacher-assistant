import enum


class UserRole(str, enum.Enum):
    """Roles a User account can hold.

    Inherits from `str` in addition to `Enum` so that SQLAlchemy
    stores and compares the lowercase `.value` string (e.g.
    "super_admin") in Postgres, rather than the uppercase member
    `.name` (e.g. "SUPER_ADMIN"). This must match exactly wherever
    role strings are referenced elsewhere, such as the CHECK
    constraint in the User model.
    """

    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    
class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    
class LessonStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"