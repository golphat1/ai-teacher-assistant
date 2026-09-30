import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class SchoolAISettings(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "school_ai_settings"

    school_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("schools.id"), unique=True, nullable=False)
    preferred_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="anthropic")
    preferred_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    monthly_token_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)