# backend/app/models/submission_analysis.py
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class SubmissionAnalysis(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "submission_analyses"
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("student_submissions.id"), unique=True, nullable=False)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[list] = mapped_column(JSONB, nullable=False)
    weaknesses: Mapped[list] = mapped_column(JSONB, nullable=False)
    misunderstood_concepts: Mapped[list] = mapped_column(JSONB, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSONB, nullable=False)
    ai_provider_used: Mapped[str] = mapped_column(String(50), nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)