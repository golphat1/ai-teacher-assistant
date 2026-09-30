import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.ai_request_log import AIRequestLog
from app.models.enums import UserRole
from app.models.school import School
from app.models.user import User
from app.services.ai_budget_service import AIBudgetService


def test_no_budget_configured_never_blocks(db_session):
    school = School(name="No Budget School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    AIBudgetService(db_session).check_budget(school.id)  # should not raise


def test_budget_exceeded_raises(db_session):
    school = School(name="Budget School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    teacher = User(school_id=school.id, email="t@example.com", hashed_password=hash_password("x"), full_name="T", role=UserRole.TEACHER)
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)

    service = AIBudgetService(db_session)
    service.settings_repo.update(school.id, monthly_token_budget=100)

    db_session.add(
        AIRequestLog(
            school_id=school.id, user_id=teacher.id, purpose="lesson_generation", provider="anthropic",
            model="claude-sonnet-4-6", prompt_tokens=80, completion_tokens=30, latency_ms=100, status="success",
        )
    )
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        service.check_budget(school.id)
    assert exc_info.value.status_code == 402


def test_school_admin_can_update_ai_settings_teacher_cannot(client, db_session):
    school = School(name="Admin School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    admin = User(
        school_id=school.id, email="admin@example.com", hashed_password=hash_password("supersecret1"),
        full_name="Admin", role=UserRole.SCHOOL_ADMIN,
    )
    db_session.add(admin)
    db_session.commit()

    admin_login = client.post(
        "/auth/login", json={"email": "admin@example.com", "password": "supersecret1", "school_id": str(school.id)}
    ).json()

    response = client.patch(
        "/schools/me/ai-settings", json={"monthly_token_budget": 50000},
        headers={"Authorization": f"Bearer {admin_login['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["monthly_token_budget"] == 50000

    client.post("/auth/register/teacher", json={"email": "t2@example.com", "password": "supersecret1", "full_name": "T2", "school_id": str(school.id)})
    teacher_login = client.post(
        "/auth/login", json={"email": "t2@example.com", "password": "supersecret1", "school_id": str(school.id)}
    ).json()

    forbidden = client.patch(
        "/schools/me/ai-settings", json={"monthly_token_budget": 1},
        headers={"Authorization": f"Bearer {teacher_login['access_token']}"},
    )
    assert forbidden.status_code == 403