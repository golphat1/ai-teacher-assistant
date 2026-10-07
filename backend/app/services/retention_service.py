from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.ai_request_log_repository import AIRequestLogRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository


class RetentionService:
    """Runs purge operations for data categories with a defined retention policy.
    Deliberately does NOT touch student_submissions, submission_answers,
    submission_analyses, or score_override_audits — those are retained
    indefinitely by policy (see Stage D documentation), not merely 'not yet implemented'."""

    def __init__(self, db: Session):
        self.db = db
        self.ai_logs = AIRequestLogRepository(db)
        self.refresh_tokens = RefreshTokenRepository(db)

    def purge_ai_request_logs(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.ai_request_log_retention_days)
        deleted = self.ai_logs.purge_older_than(cutoff)
        self.db.commit()
        return deleted

    def purge_expired_refresh_tokens(self) -> int:
        deleted = self.refresh_tokens.purge_expired(datetime.now(timezone.utc))
        self.db.commit()
        return deleted

    def run_all(self) -> dict:
        return {
            "ai_request_logs_deleted": self.purge_ai_request_logs(),
            "refresh_tokens_deleted": self.purge_expired_refresh_tokens(),
        }