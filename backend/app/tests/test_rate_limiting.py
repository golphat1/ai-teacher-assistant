import pytest

from app.core.rate_limit import limiter


@pytest.fixture()
def rate_limiting_enabled():
    limiter.enabled = True
    try:
        yield
    finally:
        limiter.enabled = False


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