import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class ClassAnalyticsSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "class_analytics_snapshots"

    class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("class.id"), nullable=False, index=True)
    average_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    submission_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score_distribution: Mapped[list] = mapped_column(JSONB, nullable=False)
    common_misconceptions: Mapped[list] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)