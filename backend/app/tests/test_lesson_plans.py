from app.tests.test_classes import _setup_teacher_and_student


VALID_PAYLOAD = {
    "topic": "Poetry",
    "subject": "English",
    "grade": "10",
    "duration_minutes": 45,
    "student_count": 25,
    "ability_level": "mixed",
}


def _teacher_token_and_class(client, db_session):
    token, _ = _setup_teacher_and_student(client, db_session)
    class_resp = client.post(
        "/classes",
        json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    return token, class_resp["id"]


def test_generate_requires_auth(client, db_session):
    response = client.post("/api/v1/lesson-plans/generate", json=VALID_PAYLOAD)
    assert response.status_code in (401, 403)


def test_generate_success_returns_mock_content(client, db_session):
    token, class_id = _teacher_token_and_class(client, db_session)
    payload = {**VALID_PAYLOAD, "class_id": class_id}
    response = client.post(
        "/api/v1/lesson-plans/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["is_mock"] is True
    assert body["topic"] == "Poetry"
    assert len(body["learning_objectives"]) > 0
    assert len(body["teaching_activities"]) > 0
    assert body["assessment_questions"][0]["question_type"] in ("mcq", "short_answer", "essay")


def test_generate_rejects_invalid_student_count(client, db_session):
    token, class_id = _teacher_token_and_class(client, db_session)
    payload = {**VALID_PAYLOAD, "class_id": class_id, "student_count": 0}
    response = client.post(
        "/api/v1/lesson-plans/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_generate_rejects_oversized_duration(client, db_session):
    token, class_id = _teacher_token_and_class(client, db_session)
    payload = {**VALID_PAYLOAD, "class_id": class_id, "duration_minutes": 500}
    response = client.post(
        "/api/v1/lesson-plans/generate",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_student_role_cannot_generate(client, db_session):
    from app.models.school import School

    school = School(name="Test High 2")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post(
        "/auth/register/student",
        json={"email": "s2@example.com", "password": "supersecret1", "full_name": "S2", "school_id": str(school.id)},
    )
    login = client.post(
        "/auth/login",
        json={"email": "s2@example.com", "password": "supersecret1"},
    ).json()

    response = client.post(
        "/api/v1/lesson-plans/generate",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 403