import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole
from app.models.student_profile import StudentProfile
from app.models.teacher_profile import TeacherProfile
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user = UserRepository(db)
        self.refresh_token = RefreshTokenRepository(db)

    # ---------- registration ----------

    def register_teacher(
        self, *, email: str, password: str, full_name: str, school_id: uuid.UUID
    ) -> User:
        return self._register(
            email=email,
            password=password,
            full_name=full_name,
            school_id=school_id,
            role=UserRole.TEACHER,
        )

    def register_student(
        self, *, email: str, password: str, full_name: str, school_id: uuid.UUID
    ) -> User:
        return self._register(
            email=email,
            password=password,
            full_name=full_name,
            school_id=school_id,
            role=UserRole.STUDENT,
        )

    def _register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        school_id: uuid.UUID,
        role: UserRole,
    ) -> User:
        existing = self.user.get_by_email(email, school_id=school_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists at this school.",
            )

        user = self.user.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            school_id=school_id,
        )

        if role == UserRole.TEACHER:
            self.db.add(TeacherProfile(user_id=user.id))
        elif role == UserRole.STUDENT:
            self.db.add(StudentProfile(user_id=user.id))

        self.db.commit()
        self.db.refresh(user)
        return user

    # ---------- login / tokens ----------

    def authenticate(
        self, *, email: str, password: str, school_id: uuid.UUID | None = None
    ) -> User:
        user = self.user.get_by_email(email, school_id=school_id)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled."
            )
        return user

    def issue_token(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            user_id=user.id, role=user.role.value, school_id=user.school_id
        )

        jti = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # Sign first: if signing fails, no database row is left behind.
        refresh_token = create_refresh_token(
            user_id=user.id, jti=jti, expires_at=expires_at
        )

        self.refresh_token.create(user_id=user.id, token_id=jti, expires_at=expires_at)
        self.db.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        payload = self._decode_refresh(refresh_token)
        jti = uuid.UUID(payload["jti"])
        user_id = uuid.UUID(payload["sub"])

        record = self.refresh_token.get_valid(jti)
        if record is None or record.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
            )

        user = self.user.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
            )

        # Rotation: revoke the old token only now that a replacement will be issued.
        self.refresh_token.revoke(jti)
        return self.issue_token(user)  # commits the revoke and the new row together

    def logout(self, refresh_token: str) -> None:
        payload = self._decode_refresh(refresh_token)
        jti = uuid.UUID(payload["jti"])
        self.refresh_token.revoke(jti)
        self.db.commit()

    @staticmethod
    def _decode_refresh(refresh_token: str) -> dict:
        try:
            payload = decode_refresh_token(refresh_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
            )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type."
            )
        # The callers rely on these claims, so make sure they exist and are valid UUIDs.
        try:
            uuid.UUID(payload["jti"])
            uuid.UUID(payload["sub"])
        except (KeyError, ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
            )
        return payload