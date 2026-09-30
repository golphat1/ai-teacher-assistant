import uuid

from sqlalchemy.orm import Session

from app.models.school_ai_settings import SchoolAISettings


class SchoolAISettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, school_id: uuid.UUID) -> SchoolAISettings:
        row = self.db.query(SchoolAISettings).filter(SchoolAISettings.school_id == school_id).first()
        if row is None:
            row = SchoolAISettings(school_id=school_id)
            self.db.add(row)
            self.db.flush()
        return row

    def update(self, school_id: uuid.UUID, **fields) -> SchoolAISettings:
        row = self.get_or_create(school_id)
        for key, value in fields.items():
            if value is not None:
                setattr(row, key, value)
        self.db.flush()
        return row