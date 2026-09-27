from unittest.mock import patch

from app.ai.providers.base import AIGenerationError


def _teacher_token(client, db_session, email="teacher@example.com"):
    from app.models.school import School

    school = School(name="Test High")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post(
        "/auth/register/teacher",
        json={"email": email, "password": "supersecret1", "full_name": "T", "school_id": str(school.id)},
    )
    login = client.post(
        "/auth/login", json={"email": email, "password": "supersecret1", "school_id": str(school.id)}
    ).json()
    return login["access_token"]


VALID_PAYLOAD = {
    "grade": "Grade 10", "subject": "English", "topic": "Poetry",
    "student_count": 40, "duration_minutes": 60, "ability_level": "mixed",
}


def test_generate_falls_back_to_mock_when_use_mock_ai_true(client, db_session):
    # USE_MOCK_AI defaults to true in test .env — orchestrator is never even called.
    token = _teacher_token(client, db_session)
    response = client.post(
        "/api/v1/lesson-plans/generate", json=VALID_PAYLOAD, headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())
    assert response.status_code == 201
    assert response.json()["is_mock"] is True


def test_generate_returns_502_when_ai_call_fails(client, db_session):
    token = _teacher_token(client, db_session)
    with patch("app.core.config.settings.use_mock_ai", False), \
         patch(
             "app.services.lesson_plan_service.AIOrchestrator.generate_lesson_content",
             side_effect=AIGenerationError("simulated failure"),
         ):
        response = client.post(
            "/api/v1/lesson-plans/generate", json=VALID_PAYLOAD, headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 502