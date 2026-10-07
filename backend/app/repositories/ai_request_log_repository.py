from sqlalchemy.orm import Session
from app.models.ai_request_log import AIRequestLog
from datetime import datetime


class AIRequestLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, **fields) -> AIRequestLog:
        entry = AIRequestLog(**fields)
        self.db.add(entry)
        self.db.flush()
        return entry
    
    def purge_older_than(self, cutoff: datetime) -> int:
        deleted_count = self.db.query(AIRequestLog).filter(AIRequestLog.created_at < cutoff).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count