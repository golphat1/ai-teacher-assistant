from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    StudentRegisterRequest,
    TeacherRegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/teacher", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_teacher(payload: TeacherRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_teacher(
        email=payload.email, password=payload.password, full_name=payload.full_name, school_id=payload.school_id
    )
    return user

@router.post("/register/student", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_student(payload: StudentRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register_student(
        email=payload.email, password=payload.password, full_name=payload.full_name, school_id=payload.school_id
    )
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.authenticate(
        email=payload.email, password=payload.password, school_id=payload.school_id
    )
    return service.issue_token(user)

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_access_token(payload.refresh_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/teacher-only-ping", dependencies=[Depends(require_roles(UserRole.TEACHER))])
def teacher_only_ping():
    return {"message": "You are authenticated as a teacher."}