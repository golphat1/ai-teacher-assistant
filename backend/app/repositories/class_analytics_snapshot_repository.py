import uuid

from sqlalchemy.orm import Session

from app.models.class_analytics_snapshot import ClassAnalyticsSnapshot


class ClassAnalyticsSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest(self, class_id: uuid.UUID) -> ClassAnalyticsSnapshot | None:
        return (
            self.db.query(ClassAnalyticsSnapshot)
            .filter(ClassAnalyticsSnapshot.class_id == class_id)
            .order_by(ClassAnalyticsSnapshot.generated_at.desc())
            .first()
        )

    def create(self, **fields) -> ClassAnalyticsSnapshot:
        snapshot = ClassAnalyticsSnapshot(**fields)
        self.db.add(snapshot)
        self.db.flush()
        return snapshot