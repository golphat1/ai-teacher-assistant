def _setup_teacher_and_student(client, db_session):
    from app.models.school import School

    school = School(name="Test High")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post(
        "/auth/register/teacher",
        json={"email": "t@example.com", "password": "supersecret1", "full_name": "T", "school_id": str(school.id)},
    )
    teacher_login = client.post(
        "/auth/login",
        json={"email": "t@example.com", "password": "supersecret1", "full_name": "T", "school_id": str(school.id)},
    ).json()

    student_resp = client.post(
        "/auth/register/student",
        json={"email": "s@example.com", "password": "supersecret1", "full_name": "S", "school_id": str(school.id)},
    ).json()

    return teacher_login["access_token"], student_resp["id"]


def test_teacher_can_create_class(client, db_session):
    token, _ = _setup_teacher_and_student(client, db_session)
    response = client.post(
        "/classes",
        json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Grade 10 - A"


def test_student_cannot_create_class(client, db_session):
    _, student_id = _setup_teacher_and_student(client, db_session)
    login = client.post(
        "/auth/login",
        json={"email": "s@example.com", "password": "supersecret1"},
    ).json()
    response = client.post(
        "/classes",
        json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 403


def test_enroll_student_success(client, db_session):
    token, student_id = _setup_teacher_and_student(client, db_session)
    class_resp = client.post(
        "/classes", json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    response = client.post(
        f"/classes/{class_resp['id']}/enroll",
        json={"student_id": student_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_enroll_same_student_twice_fails(client, db_session):
    token, student_id = _setup_teacher_and_student(client, db_session)
    class_resp = client.post(
        "/classes", json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {token}"},
    ).json()

    client.post(f"/classes/{class_resp['id']}/enroll", json={"student_id": student_id}, headers={"Authorization": f"Bearer {token}"})
    response = client.post(f"/classes/{class_resp['id']}/enroll", json={"student_id": student_id}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 409