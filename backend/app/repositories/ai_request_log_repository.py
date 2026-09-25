from sqlalchemy.orm import Session
from app.models.ai_request_log import AIRequestLog


class AIRequestLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, **fields) -> AIRequestLog:
        entry = AIRequestLog(**fields)
        self.db.add(entry)
        self.db.flush()
        return entry