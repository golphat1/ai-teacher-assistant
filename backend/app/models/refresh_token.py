import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

# Same circular-import guard as in school.py: User needs this module
# for type hints only, not at runtime, since RefreshToken -> User and
# User -> RefreshToken would otherwise import each other in a loop.
if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """RefreshToken model representing a single issued refresh token.

    One row per token issued to a user. `revoked` lets us invalidate
    a token (e.g. on logout or detected reuse) without deleting the
    row, so we keep an audit trail of token history per user.
    """

    __tablename__ = "refresh_tokens"

    # Which user this token belongs to. Indexed since the most common
    # query pattern is "find all tokens for this user" (e.g. to revoke
    # all sessions on password change).
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # When this token stops being valid, regardless of `revoked`.
    # Checked at auth time so an unused-but-expired token can't be
    # replayed even if nobody explicitly revoked it.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Explicit revocation flag, set to True on logout or on detecting
    # token reuse (a strong signal of a stolen refresh token).
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Many-to-one back to the owning user. `back_populates` must match
    # the name of the corresponding relationship on User (commonly
    # something like `refresh_tokens: Mapped[list["RefreshToken"]]`) —
    # SQLAlchemy uses this pairing to keep both sides in sync in memory.
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")