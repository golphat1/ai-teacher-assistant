def _register_teacher(client, school_id, email="teacher@example.com"):
    return client.post(
        "/auth/register/teacher",
        json={"email": email, "password": "supersecret1", "full_name": "Ada Teacher", "school_id": school_id},
    )
    
def _make_school(db_session):
    from app.models.school import School
    
    school = School(name="Test High School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)
    return school

def test_register_teacher_success(client, db_session):
    school = _make_school(db_session)
    response = _register_teacher(client, str(school.id))
    
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "teacher@example.com"
    assert body["role"] == "teacher"
    assert "hashed_password" not in  body
    assert "password" not in body
    
def test_register_duplicate_email_fails(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
    response = _register_teacher(client, str(school.id))
    
    assert response.status_code == 409
    
def test_login_success_and_returns_tokens(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
    
    response = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": "supersecret1", "school_id": str(school.id)},
    )
    
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    
def test_login_wrong_password_fails(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
     
    response = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": "wrongpassword", "school_id": str(school.id)},
     )
    assert response.status_code == 401
    
def test_me_requires_valid_token(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
    login_resp = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": "supersecret1", "school_id": str(school.id)},
    )
    access_token = login_resp.json()["access_token"]
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "teacher@example.com"
    
    unauthorized = client.get("/auth/me")
    assert unauthorized.status_code in (401, 403)
    
def test_refresh_rotates_token_and_old_one_becomes_invalid(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
    login_resp = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": "supersecret1", "school_id": str(school.id)},
    )
    old_refresh = login_resp.json()["refresh_token"]
    
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert new_tokens["refresh_token"] != old_refresh
    
    reuse_resp = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse_resp.status_code == 401
    
def test_logout_revokes_refresh_token(client, db_session):
    school = _make_school(db_session)
    _register_teacher(client, str(school.id))
    login_resp = client.post(
        "/auth/login",
        json={"email": "teacher@example.com", "password": "supersecret1", "school_id": str(school.id)},
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    
    logout_resp = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204
        
    reuse_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_resp.status_code == 401
    
def test_role_restricted_endpoint_blocks_students(client, db_session):
    school = _make_school(db_session)
    client.post(
        "/auth/register/student",
        json={
        "email": "student@example.com",
        "password": "supersecret1",
        "full_name": "Test Student",
        "school_id": str(school.id),
    },
    
    )
    login_resp = client.post(
        "/auth/login",
        json={"email": "student@example.com", "password": "supersecret1", "school_id": str(school.id)},
    )
    access_token = login_resp.json()["access_token"]
    
    response = client.get("/auth/teacher-only-ping", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403