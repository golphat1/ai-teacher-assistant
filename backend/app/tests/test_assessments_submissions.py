import uuid


def _register_and_login(client, db_session, *, role, email, school_id):
    endpoint = "/auth/register/teacher" if role == "teacher" else "/auth/register/student"
    resp = client.post(endpoint, json={"email": email, "password": "supersecret1", "full_name": "X", "school_id": school_id})
    user_id = resp.json()["id"]
    login = client.post("/auth/login", json={"email": email, "password": "supersecret1", "school_id": school_id}).json()
    return login["access_token"], user_id


def _full_setup(client, db_session):
    from app.models.school import School

    school = School(name="Test High")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)
    school_id = str(school.id)

    teacher_token, teacher_id = _register_and_login(client, db_session, role="teacher", email="t@example.com", school_id=school_id)
    student_token, student_id = _register_and_login(client, db_session, role="student", email="s@example.com", school_id=school_id)

    class_resp = client.post(
        "/classes", json={"name": "Grade 10 - A", "subject": "English", "grade": "10"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()
    client.post(
        f"/classes/{class_resp['id']}/enroll", json={"student_id": student_id},
        headers={"Authorization": f"Bearer {teacher_token}"},
    )

    lesson_resp = client.post(
        "/api/v1/lesson-plans/generate",
        json={"grade": "Grade 10", "subject": "English", "topic": "Poetry", "student_count": 40, "duration_minutes": 60, "ability_level": "mixed"},
        headers={"Authorization": f"Bearer {teacher_token}"},
    ).json()

    return {
        "school_id": school_id, "teacher_token": teacher_token, "teacher_id": teacher_id,
        "student_token": student_token, "student_id": student_id,
        "class_id": class_resp["id"], "lesson_plan_id": lesson_resp["lesson_plan_id"],
    }


def _create_assessment_and_assignment(client, ctx, headers_t):
    assessment = client.post(
        "/assessments",
        json={
            "lesson_plan_id": ctx["lesson_plan_id"], "title": "Poetry Quiz", "assessment_type": "formative",
            "questions": [{"question_text": "What is a metaphor?", "question_type": "short_answer", "max_score": 5, "order_index": 0}],
        },
        headers=headers_t,
    ).json()
    assignment = client.post(
        "/assignments", json={"assessment_id": assessment["id"], "class_id": ctx["class_id"]}, headers=headers_t
    ).json()
    return assessment, assignment


def test_full_assessment_assignment_submission_flow(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    assert "correct_answer_text" not in assessment["questions"][0]
    question_id = assessment["questions"][0]["id"]

    submit_resp = client.post(
        f"/assignments/{assignment['id']}/submissions",
        json={"answers": [{"question_id": question_id, "answer_text": "A comparison without using like or as."}]},
        headers=headers_s,
    )
    assert submit_resp.status_code == 201

    duplicate_resp = client.post(
        f"/assignments/{assignment['id']}/submissions",
        json={"answers": [{"question_id": question_id, "answer_text": "Second attempt."}]},
        headers=headers_s,
    )
    assert duplicate_resp.status_code == 409

    list_resp = client.get(f"/assignments/{assignment['id']}/submissions", headers=headers_t)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


def test_non_enrolled_student_cannot_submit(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    other_token, _ = _register_and_login(client, db_session, role="student", email="other@example.com", school_id=ctx["school_id"])

    assessment, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    response = client.post(
        f"/assignments/{assignment['id']}/submissions",
        json={"answers": [{"question_id": assessment["questions"][0]["id"], "answer_text": "..."}]},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


def test_submit_rejects_unknown_question_id(client, db_session):
    ctx = _full_setup(client, db_session)
    headers_t = {"Authorization": f"Bearer {ctx['teacher_token']}"}
    headers_s = {"Authorization": f"Bearer {ctx['student_token']}"}

    _, assignment = _create_assessment_and_assignment(client, ctx, headers_t)
    response = client.post(
        f"/assignments/{assignment['id']}/submissions",
        json={"answers": [{"question_id": str(uuid.uuid4()), "answer_text": "..."}]},
        headers=headers_s,
    )
    assert response.status_code == 422