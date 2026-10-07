from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.services.retention_service import RetentionService

router = APIRouter(prefix="/admin/retention", tags=["admin"])


@router.post("/purge", dependencies=[Depends(require_roles(UserRole.SUPER_ADMIN))])
def run_retention_purge(db: Session = Depends(get_db)):
    return RetentionService(db).run_all()