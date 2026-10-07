from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.models.ai_request_log import AIRequestLog
from app.models.enums import UserRole
from app.models.refresh_token import RefreshToken
from app.models.school import School
from app.models.user import User
from app.services.retention_service import RetentionService


def _make_user(db_session, school, role=UserRole.TEACHER, email="t@example.com"):
    user = User(school_id=school.id if role != UserRole.SUPER_ADMIN else None,
                email=email, hashed_password=hash_password("supersecret1"), full_name="X", role=role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_purge_ai_request_logs_removes_old_but_keeps_recent(db_session):
    school = School(name="Retention School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)
    teacher = _make_user(db_session, school)

    old_log = AIRequestLog(
        school_id=school.id, user_id=teacher.id, purpose="lesson_generation", provider="anthropic",
        model="claude-sonnet-4-6", prompt_tokens=10, completion_tokens=10, latency_ms=5, status="success",
    )
    db_session.add(old_log)
    db_session.commit()
    db_session.refresh(old_log)
    # created_at has a server_default of now() — manually backdate it for this test.
    db_session.query(AIRequestLog).filter(AIRequestLog.id == old_log.id).update(
        {"created_at": datetime.now(timezone.utc) - timedelta(days=200)}
    )

    recent_log = AIRequestLog(
        school_id=school.id, user_id=teacher.id, purpose="lesson_generation", provider="anthropic",
        model="claude-sonnet-4-6", prompt_tokens=5, completion_tokens=5, latency_ms=5, status="success",
    )
    db_session.add(recent_log)
    db_session.commit()

    deleted = RetentionService(db_session).purge_ai_request_logs()
    assert deleted == 1

    remaining = db_session.query(AIRequestLog).all()
    assert len(remaining) == 1
    assert remaining[0].id == recent_log.id


def test_purge_expired_refresh_tokens(db_session):
    school = School(name="Token Retention School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)
    teacher = _make_user(db_session, school, email="t2@example.com")

    expired = RefreshToken(user_id=teacher.id, expires_at=datetime.now(timezone.utc) - timedelta(days=1), revoked=False)
    revoked = RefreshToken(user_id=teacher.id, expires_at=datetime.now(timezone.utc) + timedelta(days=5), revoked=True)
    active = RefreshToken(user_id=teacher.id, expires_at=datetime.now(timezone.utc) + timedelta(days=5), revoked=False)
    db_session.add_all([expired, revoked, active])
    db_session.commit()

    deleted = RetentionService(db_session).purge_expired_refresh_tokens()
    assert deleted == 2  # expired AND revoked, not the still-active one

    remaining = db_session.query(RefreshToken).all()
    assert len(remaining) == 1
    assert remaining[0].id == active.id


def test_purge_endpoint_requires_super_admin(client, db_session):
    school = School(name="Endpoint Retention School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post("/auth/register/teacher", json={"email": "t3@example.com", "password": "supersecret1", "full_name": "T", "school_id": str(school.id)})
    teacher_login = client.post("/auth/login", json={"email": "t3@example.com", "password": "supersecret1", "school_id": str(school.id)}).json()

    forbidden = client.post("/admin/retention/purge", headers={"Authorization": f"Bearer {teacher_login['access_token']}"})
    assert forbidden.status_code == 403

    admin = _make_user(db_session, school, role=UserRole.SUPER_ADMIN, email="super@example.com")
    admin_login = client.post("/auth/login", json={"email": "super@example.com", "password": "supersecret1"}).json()

    allowed = client.post("/admin/retention/purge", headers={"Authorization": f"Bearer {admin_login['access_token']}"})
    assert allowed.status_code == 200
    assert "ai_request_logs_deleted" in allowed.json()