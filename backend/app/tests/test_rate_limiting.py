import pytest

from app.core.rate_limit import limiter


@pytest.fixture
def rate_limiting_enabled():
    previous = limiter.enabled
    limiter.reset()
    limiter.enabled = True
    try:
        yield
    finally:
        limiter.enabled = previous
        limiter.reset()


def test_login_is_rate_limited_after_five_attempts(client, db_session, rate_limiting_enabled):
    from app.models.school import School

    school = School(name="Rate Limit Test School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post(
        "/auth/register/teacher",
        json={"email": "rl@example.com", "password": "supersecret1", "full_name": "RL", "school_id": str(school.id)},
    )

    login_payload = {"email": "rl@example.com", "password": "wrong-password", "school_id": str(school.id)}

    for _ in range(5):
        response = client.post("/auth/login", json=login_payload)
        assert response.status_code == 401  # wrong password, but not yet rate-limited

    sixth_response = client.post("/auth/login", json=login_payload)
    assert sixth_response.status_code == 429
    assert "retry-after" in {h.lower() for h in sixth_response.headers.keys()}


def test_rate_limit_key_is_independent_per_route(client, db_session, rate_limiting_enabled):
    """Confirms exhausting the login limit doesn't also block an unrelated route
    (e.g. register), since each is limited independently."""
    from app.models.school import School

    school = School(name="Rate Limit Test School 2")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    for _ in range(6):
        client.post("/auth/login", json={"email": "nobody@example.com", "password": "x", "school_id": str(school.id)})

    register_response = client.post(
        "/auth/register/teacher",
        json={"email": "still-works@example.com", "password": "supersecret1", "full_name": "X", "school_id": str(school.id)},
    )
    assert register_response.status_code == 201
    
def test_ai_endpoint_rate_limit_is_keyed_per_user_not_per_ip(client, db_session, rate_limiting_enabled):
    """Two different users hitting the SAME test client (same effective IP, since
    TestClient requests all originate from the same address) must have INDEPENDENT
    rate-limit buckets on an AI-triggering route — proving the fix actually changed
    the keying behavior, not just that the route is still rate-limited at all."""
    from app.tests.test_lesson_plans_with_ai import VALID_PAYLOAD

    from app.models.school import School
    school = School(name="Per User Keying School")
    db_session.add(school)
    db_session.commit()
    db_session.refresh(school)

    client.post("/auth/register/teacher", json={"email": "u1@example.com", "password": "supersecret1", "full_name": "U1", "school_id": str(school.id)})
    client.post("/auth/register/teacher", json={"email": "u2@example.com", "password": "supersecret1", "full_name": "U2", "school_id": str(school.id)})
    token1 = client.post("/auth/login", json={"email": "u1@example.com", "password": "supersecret1", "school_id": str(school.id)}).json()["access_token"]
    token2 = client.post("/auth/login", json={"email": "u2@example.com", "password": "supersecret1", "school_id": str(school.id)}).json()["access_token"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Exhaust user 1's bucket (limit is 10/minute on this route).
    for _ in range(10):
        client.post("/api/v1/lesson-plans/generate", json=VALID_PAYLOAD, headers=headers1)

    user1_blocked = client.post("/api/v1/lesson-plans/generate", json=VALID_PAYLOAD, headers=headers1)
    assert user1_blocked.status_code == 429

    # User 2, same IP (same TestClient), completely separate bucket — must NOT be blocked.
    user2_still_allowed = client.post("/api/v1/lesson-plans/generate", json=VALID_PAYLOAD, headers=headers2)
    assert user2_still_allowed.status_code in (201, 502)  # 201 if mock/real succeeds, 502 only if a real AI call fails — either way, NOT 429