import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, *, user_id: uuid.UUID, token_id: uuid.UUID, expires_at: datetime) -> RefreshToken:
        record = RefreshToken(id=token_id, user_id=user_id, expires_at=expires_at, revoked=False)
        self.db.add(record)
        self.db.flush()
        return record
    
    def get_valid(self, token_id: uuid.UUID) -> RefreshToken | None:
        record = self.db.get(RefreshToken, token_id)
        if record is None or record.revoked or record.expires_at < datetime.now(timezone.utc):
            return None
        return record
    
    def revoke(self, token_id: uuid.UUID) -> None:
        record = self.db.get(RefreshToken, token_id)
        if record:
            record.revoked = True
            self.db.flush()