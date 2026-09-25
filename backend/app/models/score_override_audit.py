import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class ScoreOverrideAudit(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "score_override_audits"
    submission_answer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("submission_answers.id"), nullable=False)
    previous_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    new_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    overridden_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)