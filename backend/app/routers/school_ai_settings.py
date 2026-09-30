from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.school_ai_settings_repository import SchoolAISettingsRepository
from app.schemas.school_ai_settings import SchoolAISettingsRead, SchoolAISettingsUpdateRequest
from app.services.ai_budget_service import AIBudgetService

router = APIRouter(prefix="/schools/me", tags=["school-ai-settings"])


@router.get("/ai-settings", response_model=SchoolAISettingsRead)
def get_ai_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = SchoolAISettingsRepository(db).get_or_create(current_user.school_id)
    db.commit()
    return row


@router.patch("/ai-settings", response_model=SchoolAISettingsRead, dependencies=[Depends(require_roles(UserRole.SCHOOL_ADMIN))])
def update_ai_settings(payload: SchoolAISettingsUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = SchoolAISettingsRepository(db).update(current_user.school_id, **payload.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(row)
    return row


@router.get("/ai-usage")
def get_ai_usage(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AIBudgetService(db).get_usage_summary(current_user.school_id)