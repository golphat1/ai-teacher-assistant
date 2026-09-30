import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.pricing import estimate_cost_usd
from app.models.ai_request_log import AIRequestLog
from app.repositories.school_ai_settings_repository import SchoolAISettingsRepository


class AIBudgetService:
    def __init__(self, db: Session):
        self.db = db
        self.settings_repo = SchoolAISettingsRepository(db)

    def check_budget(self, school_id: uuid.UUID) -> None:
        settings_row = self.settings_repo.get_or_create(school_id)
        if settings_row.monthly_token_budget is None:
            return  # no cap configured — unrestricted

        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        used = (
            self.db.query(func.coalesce(func.sum(AIRequestLog.prompt_tokens + AIRequestLog.completion_tokens), 0))
            .filter(
                AIRequestLog.school_id == school_id,
                AIRequestLog.status == "success",
                AIRequestLog.created_at >= month_start,
            )
            .scalar()
        )

        if used >= settings_row.monthly_token_budget:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="This school's monthly AI usage budget has been reached. Contact your administrator.",
            )

    def get_usage_summary(self, school_id: uuid.UUID) -> dict:
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        rows = (
            self.db.query(AIRequestLog)
            .filter(AIRequestLog.school_id == school_id, AIRequestLog.created_at >= month_start)
            .all()
        )

        total_prompt = sum(r.prompt_tokens for r in rows)
        total_completion = sum(r.completion_tokens for r in rows)
        total_cost = sum(
            estimate_cost_usd(r.provider, r.model, r.prompt_tokens, r.completion_tokens)
            for r in rows if r.status == "success"
        )

        by_purpose: dict[str, dict] = {}
        for r in rows:
            bucket = by_purpose.setdefault(r.purpose, {"prompt_tokens": 0, "completion_tokens": 0, "requests": 0, "errors": 0})
            bucket["prompt_tokens"] += r.prompt_tokens
            bucket["completion_tokens"] += r.completion_tokens
            bucket["requests"] += 1
            if r.status == "error":
                bucket["errors"] += 1

        settings_row = self.settings_repo.get_or_create(school_id)
        return {
            "month_start": month_start,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "estimated_cost_usd": round(total_cost, 4),
            "monthly_token_budget": settings_row.monthly_token_budget,
            "by_purpose": by_purpose,
        }